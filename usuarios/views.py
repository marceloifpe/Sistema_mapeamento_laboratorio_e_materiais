from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Usuario
import pyrebase
import re
from hashlib import sha256

# Configuração do Firebase
config = {
    "apiKey": "AIzaSyCA8jXrKcj8WezvwTOt-RXok-GkpEfsguI",
    "authDomain": "sistemamapeamentolaboratorio.firebaseapp.com",
    "databaseURL": "https://sistemamapeamentolaboratorio-default-rtdb.firebaseio.com/",
    "projectId": "sistemamapeamentolaboratorio",
    "storageBucket": "sistemamapeamentolaboratorio.firebasestorage.app",
    "messagingSenderId": "659608837270",
    "appId": "1:659608837270:web:c8f98f42a390d49cf436b7",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
database = firebase.database()

# Função para renderizar a página de login
def login(request):
    status = request.GET.get('status')
    return render(request, 'login.html', {'status': status})

# Função para renderizar a página de cadastro
def cadastro(request):
    status = request.GET.get('status')
    return render(request, 'cadastro.html', {'status': status})

# Função para validar e processar o cadastro do usuário
def valida_cadastro(request):
    nome = request.POST.get('nome')
    senha = request.POST.get('senha')
    email = request.POST.get('email')

    # Verifica se o nome e a senha têm comprimentos adequados
    if len(nome.strip()) == 0 or len(senha.strip()) == 0:
        return redirect('/auth/cadastro/?status=1')

    # Verifica se o email possui o domínio correto
    if not email.endswith('@ufrpe.br'):
        return redirect('/auth/cadastro/?status=2')

    # Verifica se a senha atende a critérios específicos
    if len(senha) < 8 or not re.search(r'[a-z]', senha) or not re.search(r'[A-Z]', senha) or not re.search(r'[0-9]', senha) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        return redirect('/auth/cadastro/?status=3')

    # Verifica se o usuário com o mesmo email já existe no banco de dados
    usuario = Usuario.objects.filter(email=email)
    if usuario.exists():
        return redirect('/auth/cadastro/?status=8')

    try:
        # Criptografa a senha antes de salvar no banco de dados
        senha_hash = sha256(senha.encode()).hexdigest()

        # Cria um novo usuário e salva no banco de dados local (Django)
        usuario = Usuario(nome=nome, senha=senha_hash, email=email)
        usuario.save()  # O Django irá gerar automaticamente o ID

        # Salvando no Firebase Realtime Database
        usuario_firebase = {
            'nome': nome,
            'email': email,
            'senha': senha_hash  # Atenção para não salvar a senha em texto claro no Firebase
        }

        # Salva os dados no Firebase
        usuario_firebase_key = database.child("usuarios").push(usuario_firebase)

        # Verifica se o usuário foi salvo corretamente no Firebase
        usuario_firebase_check = database.child("usuarios").order_by_child("email").equal_to(email).get()

        if usuario_firebase_check.val():
            print(f"Usuário {nome} foi salvo com sucesso no Firebase!")
        else:
            print(f"Erro: Usuário {nome} não encontrado no Firebase!")

        # Redireciona para a página de sucesso
        return redirect('/auth/cadastro/?status=0')
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return redirect('/auth/cadastro/?status=9')

# Função para validar o login do usuário
def valida_login(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')

    # Verifica se o email e a senha fornecidos são válidos no Firebase (em texto claro)
    try:
        # Tenta autenticar com o Firebase (em texto claro)
        firebase_user = auth.sign_in_with_email_and_password(email, senha)

        if firebase_user:
            # Se a autenticação for bem-sucedida, armazena o ID do usuário na sessão
            usuario = Usuario.objects.filter(email=email).first()
            request.session['usuario'] = usuario.id

            # Redireciona para a página de admin ou professor com base no email
            if usuario.email == 'admin@ufrpe.br':
                return redirect(f'/gestor/home/')
            else:
                return redirect(f'/professor/homee/')
        else:
            return redirect('/auth/login/?status=1')  # Redireciona para login com erro
    except Exception as e:
        print(f"Erro ao autenticar com Firebase: {e}")
        return redirect('/auth/login/?status=1')

# Função para realizar logout
def sair(request):
    request.session.flush()
    return redirect('/auth/login/')
