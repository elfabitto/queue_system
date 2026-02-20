# 🚀 Guia de Deploy Gratuito (Render + Supabase)

Para colocar este sistema no ar gratuitamente na internet para seus 15 colaboradores, usaremos duas plataformas excelentes e gratuitas: **Render** (para rodar o sistema) e **Supabase** (para o Banco de Dados PostgreSQL).

## Passo 1: Criar o Banco de Dados Gratuito no Supabase

1. Crie uma conta no [Supabase](https://supabase.com/).
2. Clique em **"New Project"**.
3. Dê um nome ao projeto (ex: `fila-interna`) e gere uma senha forte para o banco de dados. Guarde essa senha!
4. Escolha a região mais próxima de você (ex: "South America (São Paulo)") e clique em "Create new project".
5. Aguarde alguns minutos até o banco ser provisionado.
6. No menu lateral esquerdo do Supabase, vá em **Project Settings** (ícone de engrenagem) -> **Database**.
7. Na seção **Connection string**, selecione a aba **URI** e desmarque a opção "Use connection pooling".
8. Copie a linha parecida com esta:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxx.supabase.co:5432/postgres
   ```
   *(Substitua `[YOUR-PASSWORD]` pela senha que você criou no passo 3).*
   **Guarde essa URI, você precisará dela no Render!**

## Passo 2: Subir o Código para o GitHub

O Render precisa puxar seu código de algum lugar. A forma mais fácil é pelo GitHub.
1. Crie uma conta no [GitHub](https://github.com/) se não tiver.
2. Crie um novo repositório (pode ser "Private" para que ninguém veja seu código).
3. Faça o upload dos arquivos do seu projeto `queue_system` para esse repositório (pode ser arrastando os arquivos direto no site do GitHub).
   *(Não precisa subir as pastas `venv/`, `__pycache__/` e `instance/`)*

## Passo 3: Criar o Servidor no Render

1. Crie uma conta no [Render](https://render.com/).
2. Clique em **"New"** -> **"Web Service"**.
3. Conecte sua conta do GitHub e selecione o repositório que você criou no Passo 2.
4. Preencha as configurações:
   - **Name**: Nome do seu sistema (ex: `fila-sua-empresa`).
   - **Environment**: `Python`
   - **Region**: Selecione uma região próxima ou deixe a padrão.
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -k eventlet -w 1 app:app` (Isso já está no nosso arquivo `Procfile`, mas é bom garantir).
   - **Plan Type**: Selecione "Free".
5. **MUITO IMPORTANTE:** Role para baixo e clique em **"Environment Variables"** -> **"Add Environment Variable"**.
   - **Key**: `DATABASE_URL`
   - **Value**: Coloque aqui a URI que você copiou do Supabase no Passo 1!
6. Clique em **"Create Web Service"**.

## Passo 4: Primeiro Acesso (Criação do Banco de Dados)

Quando o Render terminar de construir seu aplicativo e der o status "Live", o sistema já estará pronto!

1. Acesse o URL gerado pelo Render do seu aplicativo.
2. Na primeira vez que a página abrir, o sistema vai **automaticamente** criar as tabelas no seu banco PostgreSQL no Supabase.
3. Os usuários de teste (`admin`/`123` e os colaboradores) também serão criados automaticamente neste primeiro acesso.

Você já pode fazer login e começar a usar!

## Considerações Importantes

* O plano grátis do Render "dorme" após 15 minutos sem receber acessos. O primeiro funcionário que acessar o sistema na manhã seguinte vai notar que o site demora uns 30 a 50 segundos para abrir. Depois que ele "acordar", ele volta a ficar super rápido o dia todo.
* O sistema de filas (`Flask-SocketIO`) funciona perfeitamente nessa infraestrutura porque configuramos o `gunicorn` com `eventlet` para você!
