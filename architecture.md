# Arquitetura do Sistema de Fila

## Tecnologias
- **Backend**: Python + Flask
- **Banco de Dados**: SQLite (simples, sem necessidade de configuração externa)
- **Frontend**: HTML5, CSS3 (Tailwind CSS para minimalismo), JavaScript (Vanilla)
- **Comunicação em Tempo Real**: Flask-SocketIO (para notificações e atualização da fila sem refresh)

## Estrutura de Pastas
```text
queue_system/
├── app.py              # Ponto de entrada da aplicação
├── models.py           # Definição dos modelos (User, QueueEntry, History)
├── static/
│   ├── css/            # Estilos personalizados (tema escuro)
│   ├── js/             # Lógica de notificação e atualização da fila
│   └── sounds/         # Arquivo de áudio para notificação
├── templates/
│   ├── base.html       # Template base
│   ├── login.html      # Tela de login
│   ├── index.html      # Painel do Colaborador (Fila)
│   └── admin.html      # Painel do Administrador
└── instance/           # Banco de dados SQLite
```

## Fluxo da Fila
1. Colaborador faz login.
2. Clica em "Entrar na Fila" (Status: Disponível).
3. Quando for a vez (primeiro da fila com status Disponível):
   - Notificação Sonora + Pop-up.
   - Botões "Iniciar" e "Pular" aparecem.
4. Ao clicar em "Iniciar":
   - Status muda para "Analisando".
   - Próximo da fila fica com a vez.
   - Botão "Finalizar" aparece.
5. Ao clicar em "Finalizar":
   - Registro de histórico é criado.
   - Colaborador volta para o fim da fila (Status: Disponível).
6. Ao clicar em "Sair da Fila":
   - Removido da lista ativa.
