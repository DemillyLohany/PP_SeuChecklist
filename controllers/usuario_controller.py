from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime

from models import usuario_model
from servicos.email_servicos import enviar_email

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/')
def index():
    return render_template('index.html')


@usuario_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if usuario_model.buscar_por_email(email):
            flash("Email já cadastrado! Faça login.", "error")
            return redirect(url_for('usuario.login'))

        senha_hash = generate_password_hash(senha)
        usuario_model.criar_usuario(nome, email, senha_hash)

        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for('usuario.login'))

    return render_template('cadastro.html')


@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = usuario_model.buscar_por_email(email)

        if not usuario:
            flash("Usuário não encontrado.", "error")
            return redirect(url_for('usuario.login'))

        if not check_password_hash(usuario[3], senha):
            flash("Senha incorreta.", "error")
            return redirect(url_for('usuario.login'))

        session['usuario'] = usuario[1]

        flash("Login realizado com sucesso!", "success")
        return redirect(url_for('usuario.dashboard'))

    return render_template('login.html')


@usuario_bp.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        flash("Faça login para acessar o sistema.", "info")
        return redirect(url_for('usuario.login'))

    return render_template("dashboard.html")


@usuario_bp.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Logout realizado com sucesso!.", "success")
    return redirect(url_for('usuario.index'))


@usuario_bp.route('/esqueci', methods=['GET', 'POST'])
def esqueci():
    if request.method == 'POST':
        email = request.form['email']
        user = usuario_model.buscar_por_email(email)

        if not user:
            flash("Email não encontrado.", "error")
            return redirect(url_for('usuario.esqueci'))

        token = str(uuid.uuid4())
        expira = (datetime.datetime.now() + datetime.timedelta(minutes=15)).isoformat()

        usuario_model.salvar_token(email, token, expira)

        link = url_for('usuario.resetar', token=token, _external=True)
        enviar_email(email, link)

        flash("Email de recuperação enviado!", "success")
        return redirect(url_for('usuario.login'))

    return render_template('esqueci.html')


@usuario_bp.route('/reset/<token>', methods=['GET', 'POST'])
def resetar(token):
    result = usuario_model.buscar_por_token(token)

    if not result:
        flash("Token inválido.", "error")
        return redirect(url_for('usuario.login'))

    expira = datetime.datetime.fromisoformat(result[0])

    if datetime.datetime.now() > expira:
        flash("Token expirado.", "error")
        return redirect(url_for('usuario.login'))

    if request.method == 'POST':
        nova_senha = request.form['senha']
        senha_hash = generate_password_hash(nova_senha)

        usuario_model.atualizar_senha(token, senha_hash)

        flash("Senha atualizada com sucesso!", "success")
        return redirect(url_for('usuario.login'))

    return render_template('reset.html')