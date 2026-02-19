# 🚀 Como Usar o Sistema de Fila

## ✅ Banco de Dados Criado!

O banco de dados foi criado com sucesso em: `instance/queue.db`

## 🌐 Como Acessar o Sistema

### 1. Iniciar o Servidor

Execute o comando:
```bash
python app.py
```

### 2. Abrir no Navegador

**IMPORTANTE:** Não use `0.0.0.0:5000` no navegador!

✅ **Use um destes endereços:**
- **http://localhost:5000**
- **http://127.0.0.1:5000**

> **Por quê?** O endereço `0.0.0.0` é usado apenas para o servidor escutar em todas as interfaces de rede, mas não é um endereço válido para acessar no navegador. Use `localhost` ou `127.0.0.1` em vez disso.

## 👥 Usuários Disponíveis

### Administrador
- **Usuário:** `admin`
- **Senha:** `123`

### Colaboradores
- **Usuário:** `colaborador1` | **Senha:** `123`
- **Usuário:** `colaborador2` | **Senha:** `123`
- **Usuário:** `colaborador3` | **Senha:** `123`

## 🔧 Solução de Problemas

### Erro "ERR_ADDRESS_INVALID"
- ❌ Não use: `http://0.0.0.0:5000`
- ✅ Use: `http://localhost:5000`

### Porta já em uso
Se a porta 5000 já estiver em uso, você pode:
1. Parar o processo que está usando a porta
2. Ou modificar a porta no arquivo `app.py` (última linha)

### Banco de dados não encontrado
Execute o script de inicialização:
```bash
python init_db.py
```

## 📁 Estrutura do Projeto

```
queue_system/
├── app.py              # Aplicação principal
├── models.py           # Modelos do banco de dados
├── init_db.py          # Script de inicialização do BD
├── instance/
│   └── queue.db        # Banco de dados SQLite
├── templates/          # Templates HTML
├── static/             # Arquivos estáticos (CSS, JS, sons)
└── COMO_USAR.md        # Este arquivo
```

## 🎯 Funcionalidades

- ✅ Sistema de login
- ✅ Fila de atendimento em tempo real
- ✅ Notificações sonoras
- ✅ Painel administrativo
- ✅ Histórico de atendimentos
- ✅ Estatísticas por colaborador
