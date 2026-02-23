# O eventlet precisa aplicar o monkey patch antes de todas as outras importações 
# para funcionar corretamente no Gunicorn com o PostgreSQL/SQLAlchemy.
import eventlet
eventlet.monkey_patch()

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

# Suporte a PostgreSQL no Render ou SQLite local (fallback)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # O SQLAlchemy 1.4+ requer que a URL comece com postgresql:// e o Render às vezes fornece postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # Para evitar o erro "cannot notify on un-acquired lock" com o Eventlet/Websockets
    from sqlalchemy.pool import NullPool
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'poolclass': NullPool}
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'queue.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Inicializar o banco de dados automaticamente
with app.app_context():
    from models import User # Import garantido aqui
    db.create_all()
    usuarios_iniciais = [
        {'username': 'Jarbas', 'is_admin': False},
        {'username': 'Maiara', 'is_admin': False},
        {'username': 'Mariana', 'is_admin': False},
        {'username': 'Eliene', 'is_admin': False},
        {'username': 'Lorena', 'is_admin': True},
        {'username': 'Lucas', 'is_admin': False},
        {'username': 'Carla', 'is_admin': False},
        {'username': 'Cristiane', 'is_admin': False},
        {'username': 'Julio', 'is_admin': False},
        {'username': 'Marlon', 'is_admin': False},
        {'username': 'Antonio', 'is_admin': False},
        {'username': 'Fabio', 'is_admin': False},
        {'username': 'Ingrid', 'is_admin': False},
        {'username': 'Eduarda', 'is_admin': False}
    ]
    
    for u_data in usuarios_iniciais:
        # Só cria se o usuário ainda não existir no banco
        if not User.query.filter_by(username=u_data['username']).first():
            senha = f"{u_data['username']}123"
            novo_usuario = User(username=u_data['username'], password=senha, is_admin=u_data['is_admin'])
            db.session.add(novo_usuario)
            
    # Criar também o admin genérico caso não exista, por segurança
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password='123', is_admin=True))
        
    db.session.commit()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

socketio = SocketIO(app)

user_connections = {}

@socketio.on('connect')
def on_connect():
    if current_user.is_authenticated:
        user_id = current_user.id
        user_connections[user_id] = user_connections.get(user_id, 0) + 1

@socketio.on('disconnect')
def on_disconnect():
    pass
    # Removida a lógica de auto-remoção da fila a pedido do cliente.
    # O usuário só sai da fila se clicar explicitly no botão "Sair da fila".

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
            Attendance.finished_at.isnot(None),
            Attendance.finished_at >= today_start
        ).count()
        
        # Atendimentos desta semana
        week_count = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.finished_at.isnot(None),
            Attendance.finished_at >= week_start
        ).count()
        
        # Atendimentos deste mês
        month_count = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.finished_at.isnot(None),
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
    # Tratar history explicitamente para evitar erros de renderização no template cego (usando '.colaborador' e 'duration_seconds')
    raw_history = Attendance.query.filter(Attendance.finished_at.isnot(None)).order_by(Attendance.finished_at.desc()).limit(50).all()
    history = []
    for r in raw_history:
        history.append({
            'colaborador': {'username': r.colaborador.username if hasattr(r, 'colaborador') and r.colaborador else 'Desconhecido'},
            'duration_seconds': r.duration_seconds or 0
        })
    
    stats = []
    for user in all_users:
        if not user.is_admin:
            count = Attendance.query.filter_by(user_id=user.id).filter(Attendance.finished_at.isnot(None)).count()
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

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVIDOR INICIADO COM SUCESSO!")
    print("="*60)
    print("\n📍 Acesse o sistema em seu navegador:")
    print("   👉 http://localhost:5001")
    print("   👉 http://127.0.0.1:5001")
    print("\n" + "="*60 + "\n")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
