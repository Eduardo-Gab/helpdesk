import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-de-desenvolvimento')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///helpdesk.db'
db = SQLAlchemy(app)

ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(255))
    role = db.Column(db.String(20), default='usuario')

class Chamado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    resposta = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Aberto')
    prioridade = db.Column(db.String(20), default='Media')
    data_abertura = db.Column(db.DateTime, default=datetime.now)
    data_fechamento = db.Column(db.DateTime, nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', backref='chamados')

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        chave_admin = request.form.get('chave_admin', '')
        eh_admin = bool(ADMIN_SECRET_KEY) and chave_admin == ADMIN_SECRET_KEY
        usuario = Usuario(
            nome=request.form['nome'],
            email=request.form['email'],
            senha=generate_password_hash(request.form['senha']),
            role='admin' if eh_admin else 'usuario'
        )
        db.session.add(usuario)
        db.session.commit()
        flash('Cadastro realizado! Faca login.')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            return redirect(url_for('dashboard'))
        flash('Email ou senha invalidos.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    if current_user.role == 'admin':
        chamados = Chamado.query.order_by(Chamado.data_abertura.desc()).all()
    else:
        chamados = Chamado.query.filter_by(usuario_id=current_user.id).order_by(Chamado.data_abertura.desc()).all()
    return render_template('dashboard.html', chamados=chamados)

@app.route('/chamado/novo', methods=['GET', 'POST'])
@login_required
def novo_chamado():
    if request.method == 'POST':
        chamado = Chamado(
            titulo=request.form['titulo'],
            descricao=request.form['descricao'],
            prioridade=request.form['prioridade'],
            usuario_id=current_user.id
        )
        db.session.add(chamado)
        db.session.commit()
        flash('Chamado aberto com sucesso!')
        return redirect(url_for('dashboard'))
    return render_template('novo_chamado.html')

@app.route('/chamado/<int:id>/fechar')
@login_required
def fechar_chamado(id):
    chamado = Chamado.query.get_or_404(id)
    if current_user.role != 'admin' and chamado.usuario_id != current_user.id:
        abort(403)
    chamado.status = 'Fechado'
    chamado.data_fechamento = datetime.now()
    db.session.commit()
    flash('Chamado fechado.')
    return redirect(url_for('dashboard'))

@app.route('/chamado/<int:id>/gerenciar', methods=['GET', 'POST'])
@login_required
def gerenciar_chamado(id):
    if current_user.role != 'admin':
        abort(403)
    chamado = Chamado.query.get_or_404(id)
    if request.method == 'POST':
        chamado.prioridade = request.form['prioridade']
        chamado.status = request.form['status']
        chamado.resposta = request.form['resposta']
        if chamado.status == 'Fechado' and not chamado.data_fechamento:
            chamado.data_fechamento = datetime.now()
        db.session.commit()
        flash('Chamado atualizado!')
        return redirect(url_for('dashboard'))
    return render_template('gerenciar_chamado.html', chamado=chamado)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
