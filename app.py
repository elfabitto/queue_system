from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from models import db, User, Queue, Attendance
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-fila'
# Usar caminho absoluto para evitar erros de diretório
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'queue.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password: # Simples para este projeto
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuário ou senha incorretos.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Se estiver na fila ao sair, remover da fila
    entry = Queue.query.filter_by(user_id=current_user.id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    logout_user()
    return redirect(url_for('login'))

# --- ROTAS DA FILA ---
@app.route('/')
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for('admin'))
    
    # Pegar a fila completa ordenada por tempo de entrada
    queue_list = Queue.query.order_by(Queue.entered_at.asc()).all()
    
    # Verificar se o usuário está na fila
    user_entry = Queue.query.filter_by(user_id=current_user.id).first()
    
    # Quem está na vez? O primeiro da fila que não está "Analisando" ou o primeiro de todos?
    # Segundo o requisito: "O próximo disponível já fica na vez"
    current_turn_entry = Queue.query.filter_by(status='Disponível').order_by(Queue.entered_at.asc()).first()
    
    return render_template('index.html', queue=queue_list, user_entry=user_entry, turn_user=current_turn_entry)

@app.route('/join_queue', methods=['POST'])
@login_required
def join_queue():
    if not Queue.query.filter_by(user_id=current_user.id).first():
        new_entry = Queue(user_id=current_user.id)
        db.session.add(new_entry)
        db.session.commit()
        socketio.emit('update_queue')
    return redirect(url_for('index'))

@app.route('/leave_queue', methods=['POST'])
@login_required
def leave_queue():
    entry = Queue.query.filter_by(user_id=current_user.id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
        socketio.emit('update_queue')
    return redirect(url_for('index'))

@app.route('/start_task', methods=['POST'])
@login_required
def start_task():
    entry = Queue.query.filter_by(user_id=current_user.id).first()
    if entry and entry.status == 'Disponível':
        entry.status = 'Analisando'
        
        # Criar registro de atendimento
        attendance = Attendance(user_id=current_user.id)
        db.session.add(attendance)
        db.session.commit()
        
        socketio.emit('update_queue')
    return redirect(url_for('index'))

@app.route('/finish_task', methods=['POST'])
@login_required
def finish_task():
    entry = Queue.query.filter_by(user_id=current_user.id).first()
    if entry and entry.status == 'Analisando':
        # Atualizar atendimento
        attendance = Attendance.query.filter_by(user_id=current_user.id, finished_at=None).order_by(Attendance.started_at.desc()).first()
        if attendance:
            attendance.finished_at = datetime.utcnow()
            delta = attendance.finished_at - attendance.started_at
            attendance.duration_seconds = int(delta.total_seconds())
        
        # Voltar para o fim da fila
        entry.status = 'Disponível'
        entry.entered_at = datetime.utcnow()
        db.session.commit()
        
        socketio.emit('update_queue')
    return redirect(url_for('index'))

@app.route('/skip_task', methods=['POST'])
@login_required
def skip_task():
    entry = Queue.query.filter_by(user_id=current_user.id).first()
    if entry and entry.status == 'Disponível':
        # Mover para o fim da fila sem registrar atendimento
        entry.entered_at = datetime.utcnow()
        db.session.commit()
        socketio.emit('update_queue')
    return redirect(url_for('index'))

def get_daily_stats():
    """Calcula estatísticas diárias, semanais e mensais de atendimentos por colaborador"""
    all_users = User.query.filter_by(is_admin=False).all()
    daily_stats = []
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)
    
    for user in all_users:
        # Atendimentos de hoje
        today_count = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.finished_at != None,
            Attendance.finished_at >= today_start
        ).count()
        
        # Atendimentos desta semana
        week_count = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.finished_at != None,
            Attendance.finished_at >= week_start
        ).count()
        
        # Atendimentos deste mês
        month_count = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.finished_at != None,
            Attendance.finished_at >= month_start
        ).count()
        
        daily_stats.append({
            'username': user.username,
            'today': today_count,
            'this_week': week_count,
            'this_month': month_count
        })
    
    return daily_stats

# --- ROTA ADMIN ---
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    all_users = User.query.all()
    history = Attendance.query.filter(Attendance.finished_at != None).order_by(Attendance.finished_at.desc()).limit(50).all()
    
    stats = []
    for user in all_users:
        if not user.is_admin:
            count = Attendance.query.filter_by(user_id=user.id).filter(Attendance.finished_at != None).count()
            stats.append({'id': user.id, 'username': user.username, 'count': count})
    
    # Obter estatísticas diárias
    daily_stats = get_daily_stats()
    
    # Pegar a fila completa para exibir no painel admin
    queue_list = Queue.query.order_by(Queue.entered_at.asc()).all()
        
    return render_template('admin.html', stats=stats, history=history, all_users=all_users, daily_stats=daily_stats, queue=queue_list)

@app.route('/admin/create_user', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    is_admin = 'is_admin' in request.form
    
    if User.query.filter_by(username=username).first():
        flash('Este nome de usuário já existe.')
    else:
        new_user = User(username=username, email=email, password=password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Usuário {username} criado com sucesso!')
        
    return redirect(url_for('admin'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    if user_id == current_user.id:
        flash('Você não pode excluir a si mesmo.')
        return redirect(url_for('admin'))
        
    user = User.query.get_or_404(user_id)
    
    # Remover da fila se estiver nela
    entry = Queue.query.filter_by(user_id=user_id).first()
    if entry:
        db.session.delete(entry)
        
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuário {user.username} removido.')
    
    socketio.emit('update_queue')
    return redirect(url_for('admin'))

# Inicializar Banco de Dados com alguns usuários de teste
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='123', is_admin=True)
            user1 = User(username='colaborador1', password='123')
            user2 = User(username='colaborador2', password='123')
            user3 = User(username='colaborador3', password='123')
            db.session.add_all([admin, user1, user2, user3])
            db.session.commit()

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("🚀 SERVIDOR INICIADO COM SUCESSO!")
    print("="*60)
    print("\n📍 Acesse o sistema em seu navegador:")
    print("   👉 http://localhost:5001")
    print("   👉 http://127.0.0.1:5001")
    print("\n" + "="*60 + "\n")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
