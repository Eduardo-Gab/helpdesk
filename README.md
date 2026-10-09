# Help Desk

Sistema de chamados de suporte feito com Flask, Flask-SQLAlchemy e Flask-Login, com interface em Bootstrap.

## Funcionalidades

- Cadastro e login de usuarios, com senhas armazenadas com hash
- Perfil usuario: abre chamados e acompanha apenas os proprios
- Perfil admin: ve todos os chamados, responde, altera status e prioridade
- Conta admin criada somente com uma chave secreta definida no arquivo .env

## Como rodar

1. Instale as dependencias:

        pip install -r requirements.txt

2. Copie o arquivo .env.example para .env e defina suas proprias chaves:

        SECRET_KEY=um-texto-longo-e-aleatorio
        ADMIN_SECRET_KEY=a-chave-que-so-voce-sabe

3. Inicie a aplicacao:

        python app.py

4. Acesse http://127.0.0.1:5000/cadastro. Para criar um admin, preencha o campo "Chave admin" com o valor de ADMIN_SECRET_KEY.
