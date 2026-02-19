# Guia do Banco de Dados - Sistema de Fila

Este sistema utiliza o **SQLite** como banco de dados padrão por ser simples, rápido e não exigir configuração externa, o que facilita o uso imediato no VS Code.

## 1. Onde está o banco de dados?
O banco de dados é um arquivo físico chamado `queue.db` localizado na pasta:
`queue_system/instance/queue.db`

## 2. Como visualizar os dados no VS Code?
Para abrir e ver as tabelas diretamente no VS Code, recomendo instalar a extensão:
- **Nome**: `SQLite Viewer` (ou `SQLite` de alexcvzz)
- **Como usar**: Após instalar, basta clicar com o botão direito no arquivo `queue.db` e selecionar "Open with SQLite Viewer".

## 3. Como o código se conecta ao banco?
O sistema usa o **Flask-SQLAlchemy**, um ORM (Object Relational Mapper) que facilita a comunicação. A configuração de conexão está no arquivo `app.py`:

```python
# Trecho do código no app.py
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'queue.db')
```

## 4. Como trocar para outro banco (MySQL / PostgreSQL)?
Se o seu sistema crescer e você precisar de um banco de dados mais robusto (como MySQL), a mudança é muito simples. Você só precisará:

1. Instalar o driver do banco (ex: `pip install pymysql`).
2. Alterar a linha da `SQLALCHEMY_DATABASE_URI` no `app.py`:

```python
# Exemplo para MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:senha@localhost/nome_do_banco'

# Exemplo para PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:senha@localhost/nome_do_banco'
```

O Flask-SQLAlchemy cuidará de traduzir todos os comandos Python para a linguagem específica do novo banco de dados automaticamente!

## 5. Estrutura das Tabelas
- **User**: Armazena colaboradores e administradores.
- **Queue**: Controla quem está na fila e qual o status atual.
- **Attendance**: Registra o histórico de início, fim e duração de cada tarefa.
