from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock

from .models import Usuario

class UsuariosAuthViewsTestCase(TestCase):
    """
    Suite de testes para as views de autenticação do app 'usuarios'.
    Utiliza @patch para simular as interações com o Firebase.
    """

    def setUp(self):
        self.client = Client()
        self.cadastro_url = reverse('cadastro')
        self.login_url = reverse('login')
        self.valida_cadastro_url = reverse('valida_cadastro')
        self.valida_login_url = reverse('valida_login')
        self.sair_url = reverse('sair')

    def test_pagina_login_carrega_corretamente(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_pagina_cadastro_carrega_corretamente(self):
        response = self.client.get(self.cadastro_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadastro.html')

    def test_valida_cadastro_falha_email_invalido(self):
        response = self.client.post(self.valida_cadastro_url, {
            'nome': 'Teste',
            'email': 'teste@gmail.com',
            'senha': 'Password123!'
        })
        self.assertRedirects(response, '/auth/cadastro/?status=2')

    def test_valida_cadastro_falha_senha_fraca(self):
        response = self.client.post(self.valida_cadastro_url, {
            'nome': 'Teste',
            'email': 'teste@ufrpe.br',
            'senha': '123'
        })
        self.assertRedirects(response, '/auth/cadastro/?status=3')
    
    @patch('usuarios.views.db')
    @patch('usuarios.views.auth_instance')
    @patch('usuarios.views.Usuario')
    def test_valida_cadastro_email_ja_existe(self, mock_usuario, mock_auth, mock_db):
        mock_db.collection.return_value.where.return_value.limit.return_value.get.return_value = [MagicMock()]
        response = self.client.post(self.valida_cadastro_url, {
            'nome': 'Teste',
            'email': 'existente@ufrpe.br',
            'senha': 'Password123!'
        })
        self.assertRedirects(response, '/auth/cadastro/?status=8')

    @patch('usuarios.views.db')
    @patch('usuarios.views.auth_instance')
    @patch('usuarios.views.Usuario')
    def test_valida_cadastro_sucesso(self, mock_usuario, mock_auth, mock_db):
        mock_db.collection.return_value.where.return_value.limit.return_value.get.return_value = []
        mock_auth.create_user_with_email_and_password.return_value = {'localId': 'fake-uid'}
        mock_usuario.create_user.return_value = MagicMock(id=1)
        response = self.client.post(self.valida_cadastro_url, {
            'nome': 'Novo Usuario',
            'email': 'novo@ufrpe.br',
            'senha': 'Password123!'
        })
        self.assertRedirects(response, '/auth/cadastro/?status=0')
        mock_usuario.create_user.assert_called_once_with(nome='Novo Usuario', email='novo@ufrpe.br', senha='')

    @patch('usuarios.views.db')
    @patch('usuarios.views.auth_instance')
    @patch('usuarios.views.Usuario')
    def test_valida_login_sucesso_professor(self, mock_usuario, mock_auth, mock_db):
        mock_auth.sign_in_with_email_and_password.return_value = {'localId': 'fake-uid-prof'}
        mock_user_instance = MagicMock(id=10, nome='Professor Teste', email='professor@ufrpe.br')
        mock_usuario.get_by_email.return_value = mock_user_instance
        mock_db.collection.return_value.where.return_value.limit.return_value.get.return_value = []

        response = self.client.post(self.valida_login_url, {
            'email': 'professor@ufrpe.br',
            'senha': 'Password123!'
        })
        
        # --- ALTERAÇÃO AQUI ---
        # Verificamos o status de redirecionamento e a URL de destino separadamente.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/professor/homee/')

        # Verificamos se os dados do usuário foram colocados na sessão
        self.assertEqual(self.client.session['usuario'], 10)
        self.assertEqual(self.client.session['usuario_nome'], 'Professor Teste')
        self.assertFalse(self.client.session['is_admin'])

    @patch('usuarios.views.db')
    @patch('usuarios.views.auth_instance')
    @patch('usuarios.views.Usuario')
    def test_valida_login_sucesso_admin(self, mock_usuario, mock_auth, mock_db):
        mock_auth.sign_in_with_email_and_password.return_value = {'localId': 'fake-uid-admin'}
        mock_user_instance = MagicMock(id=1, nome='Admin', email='admin@ufrpe.br')
        mock_usuario.get_by_email.return_value = mock_user_instance
        mock_db.collection.return_value.where.return_value.limit.return_value.get.return_value = [MagicMock()]
        
        response = self.client.post(self.valida_login_url, {
            'email': 'admin@ufrpe.br',
            'senha': 'Password123!'
        })
        
        # --- ALTERAÇÃO AQUI ---
        # Verificamos o status de redirecionamento e a URL de destino separadamente.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/gestor/home/')
        
        self.assertEqual(self.client.session['usuario'], 1)
        self.assertTrue(self.client.session['is_admin'])

    @patch('usuarios.views.auth_instance')
    def test_valida_login_falha(self, mock_auth):
        mock_auth.sign_in_with_email_and_password.side_effect = Exception("Firebase error")
        response = self.client.post(self.valida_login_url, {
            'email': 'teste@ufrpe.br',
            'senha': 'senhaerrada'
        })
        self.assertRedirects(response, '/auth/login/?status=1')
        self.assertNotIn('usuario', self.client.session)
    
    def test_sair_limpa_sessao_e_redireciona(self):
        session = self.client.session
        session['usuario'] = 1
        session.save()
        self.assertIn('usuario', self.client.session)
        response = self.client.get(self.sair_url)
        self.assertRedirects(response, self.login_url)
        self.assertNotIn('usuario', self.client.session)