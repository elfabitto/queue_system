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
    
    # Relacionamento com o histórico
    attendances = db.relationship('Attendance', backref='colaborador', lazy=True)

class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Disponível') # Disponível, Analisando
    entered_at = db.Column(db.DateTime, default=get_brt_time)
    
    user = db.relationship('User', backref=db.backref('queue_entry', uselist=False))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=get_brt_time)
    finished_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

class Skip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skipped_at = db.Column(db.DateTime, default=get_brt_time)
    
    user = db.relationship('User', backref=db.backref('skips', lazy=True))
