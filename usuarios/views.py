from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Usuario
import pyrebase
import re

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

# Página de Login
def login(request):
    status = request.GET.get('status')
    return render(request, 'login.html', {'status': status})

# Página de Cadastro
def cadastro(request):
    status = request.GET.get('status')
    return render(request, 'cadastro.html', {'status': status})

# Validação de Cadastro
def valida_cadastro(request):
    nome = request.POST.get('nome')
    senha = request.POST.get('senha')
    email = request.POST.get('email')

    # Validações
    if not nome or not senha or not email:
        return redirect('/auth/cadastro/?status=1')

    if not email.endswith('@ufrpe.br'):
        return redirect('/auth/cadastro/?status=2')

    if len(senha) < 8 or not re.search(r'[a-z]', senha) or not re.search(r'[A-Z]', senha) or not re.search(r'[0-9]', senha) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        return redirect('/auth/cadastro/?status=3')

    if Usuario.objects.filter(email=email).exists():
        return redirect('/auth/cadastro/?status=8')

    try:
        # Cria usuário no Firebase
        firebase_user = auth.create_user_with_email_and_password(email, senha)

        # Salva no banco local
        usuario = Usuario(nome=nome, email=email)
        usuario.save()

        # Adiciona informações extras ao Realtime Database
        database.child("usuarios").child(firebase_user['localId']).set({
            'nome': nome,
            'email': email
        })

        return redirect('/auth/cadastro/?status=0')
    except Exception as e:
        print(f"Erro no cadastro: {e}")
        return redirect('/auth/cadastro/?status=9')

# Validação de Login
def valida_login(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')

    try:
        # Autenticação no Firebase
        firebase_user = auth.sign_in_with_email_and_password(email, senha)

        # Busca o usuário no banco local
        usuario = Usuario.objects.filter(email=email).first()
        if not usuario:
            return redirect('/auth/login/?status=1')

        # Armazena o ID do usuário na sessão
        request.session['usuario'] = usuario.id

        # Redireciona com base no tipo de usuário
        if usuario.email == 'admin@ufrpe.br':
            return redirect('/gestor/home/')
        return redirect('/professor/homee/')
    except Exception as e:
        print(f"Erro ao autenticar: {e}")
        return redirect('/auth/login/?status=1')

# Logout
def sair(request):
    request.session.flush()
    return redirect('/auth/login/')
