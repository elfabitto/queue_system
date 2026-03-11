from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
import pytz

db = SQLAlchemy()

def get_brt_time():
    return datetime.now(pytz.timezone('America/Sao_Paulo')).replace(tzinfo=None)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    avatar_style = db.Column(db.String(50), default='fun-emoji')
    avatar_seed = db.Column(db.String(100), default=None)

    # Paleta de tons de pele + amarelo emoji
    NEUTRAL_BG_COLORS = ['f5cba7', 'e3a87a', 'c68642', 'a0522d', '6b3a2a', 'ffd93d']

    @property
    def avatar_url(self):
        seed = self.avatar_seed or self.username
        style = self.avatar_style or 'adventurer'
        if style.endswith('-neutral'):
            # Cor determinística baseada no seed (consistente para o mesmo usuário)
            color_index = sum(ord(c) for c in seed) % len(self.NEUTRAL_BG_COLORS)
            bg = self.NEUTRAL_BG_COLORS[color_index]
            return f'https://api.dicebear.com/9.x/{style}/svg?seed={seed}&backgroundColor={bg}'
        return f'https://api.dicebear.com/9.x/{style}/svg?seed={seed}&backgroundColor=transparent'

    # Relacionamento com o histórico
    attendances = db.relationship('Attendance', backref='colaborador', lazy=True)

class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Disponível') # Disponível, Analisando
    entered_at = db.Column(db.DateTime, default=get_brt_time)       # usado para ordenar (atualizado ao ciclar)
    first_entered_at = db.Column(db.DateTime, default=get_brt_time) # horário real de entrada, nunca muda
    left_at = db.Column(db.DateTime, nullable=True)   # hora de saída da fila
    service_type = db.Column(db.String(30), nullable=True)  # tipo de atendimento em andamento

    user = db.relationship('User', backref=db.backref('queue_entry', uselist=False))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_type = db.Column(db.String(30), nullable=True)  # Consulta, Troca de Titularidade, Criação de Matrícula
    started_at = db.Column(db.DateTime, default=get_brt_time)
    finished_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

class Skip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skipped_at = db.Column(db.DateTime, default=get_brt_time)
    
    user = db.relationship('User', backref=db.backref('skips', lazy=True))
