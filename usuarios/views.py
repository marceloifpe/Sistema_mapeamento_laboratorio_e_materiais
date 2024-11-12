from django.shortcuts import render
from django.http import HttpResponse
from .models import Usuario
from django.shortcuts import redirect
from hashlib import sha256
import re

# Função para renderizar a página de login
def login(request):
    # Obtém o parâmetro 'status' da URL, se presente
    status = request.GET.get('status')
    return render(request, 'login.html', {'status': status})

# Função para renderizar a página de cadastro
def cadastro(request):
    # Obtém o parâmetro 'status' da URL, se presente
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
    if len(usuario) > 0:
        return redirect('/auth/cadastro/?status=8')

    try:
        # Criptografa a senha antes de salvar no banco de dados
        senha = sha256(senha.encode()).hexdigest()
        usuario = Usuario(nome=nome, senha=senha, email=email)
        usuario.save()
        return redirect('/auth/cadastro/?status=0')
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return redirect('/auth/cadastro/?status=9')

# Função para validar o login do usuário
def valida_login(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    senha = sha256(senha.encode()).hexdigest()
    usuario = Usuario.objects.filter(email=email).filter(senha=senha)

    # Verifica se o usuário existe e redireciona para a página correta
    if len(usuario) == 0:
        return redirect('/auth/login/?status=1')
    else:
        # Armazena o ID do usuário na sessão
        request.session['usuario'] = usuario[0].id

    # Redireciona para a página de admin ou professor com base no email
    if usuario[0].email == 'admin@ufrpe.br':
        return redirect(f'/gestor/home/')
    else:
        return redirect(f'/professor/homee/')


def sair(request):
    request.session.flush()
    return redirect('/auth/login/')