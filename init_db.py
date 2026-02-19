"""
Script para inicializar o banco de dados do Sistema de Fila
Cria todas as tabelas e usuários padrão
"""
from app import app, db
from models import User

def init_database():
    with app.app_context():
        # Criar todas as tabelas
        print("Criando tabelas do banco de dados...")
        db.create_all()
        print("✓ Tabelas criadas com sucesso!")
        
        # Verificar se já existem usuários
        if User.query.first():
            print("⚠ Banco de dados já contém usuários. Pulando criação de usuários padrão.")
            return
        
        # Criar usuários padrão
        print("\nCriando usuários padrão...")
        admin = User(username='admin', password='123', is_admin=True)
        user1 = User(username='colaborador1', password='123')
        user2 = User(username='colaborador2', password='123')
        user3 = User(username='colaborador3', password='123')
        
        db.session.add_all([admin, user1, user2, user3])
        db.session.commit()
        
        print("✓ Usuários criados com sucesso!")
        print("\n" + "="*50)
        print("BANCO DE DADOS INICIALIZADO COM SUCESSO!")
        print("="*50)
        print("\nUsuários disponíveis:")
        print("  • Admin: username='admin', password='123'")
        print("  • Colaborador 1: username='colaborador1', password='123'")
        print("  • Colaborador 2: username='colaborador2', password='123'")
        print("  • Colaborador 3: username='colaborador3', password='123'")
        print("\nLocalização do banco: instance/queue.db")
        print("="*50)

if __name__ == '__main__':
    init_database()
