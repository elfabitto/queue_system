# Sistema de Fila Interna

Este é um sistema de fila minimalista desenvolvido em Flask para organização interna de colaboradores.

## Funcionalidades
- **Painel do Colaborador**: Interface simples para entrar na fila, iniciar tarefas, finalizar e sair.
- **Status em Tempo Real**: Notificações via Socket.IO para atualização da fila sem refresh.
- **Notificações**: Alerta sonoro e pop-up no navegador quando chega a vez do colaborador.
- **Painel Administrativo**: Visualização de estatísticas de atendimentos e histórico detalhado.
- **Tema Escuro**: Interface moderna, minimalista e responsiva.

## Como Executar
1. Certifique-se de ter o Python instalado.
2. Instale as dependências:
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-socketio eventlet
   ```
3. Execute o aplicativo:
   ```bash
   python app.py
   ```
4. Acesse no navegador: `http://localhost:5000`

## Usuários de Teste
- **Admin**: Usuário `admin` | Senha `123`
- **Colaboradores**: `colaborador1`, `colaborador2`, `colaborador3` | Senha `123`

## Estrutura do Projeto
- `app.py`: Lógica principal e rotas.
- `models.py`: Definição do banco de dados (SQLite).
- `templates/`: Arquivos HTML (Base, Index, Login, Admin).
- `static/`: Arquivos CSS, JS e Sons.
