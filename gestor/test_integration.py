from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

# Importamos todos os modelos que serão usados no fluxo
from usuarios.models import Usuario
from salas.models import Salas, Reservas

class FullUserFlowIntegrationTest(TestCase):
    """
    Teste de Integração que simula um fluxo completo de usuário,
    desde o cadastro até a verificação por um administrador.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Prepara os dados que não mudam durante o fluxo, como uma sala
        disponível para reserva e um usuário administrador já existente.
        """
        # A sala que nosso professor irá reservar
        cls.sala_para_reservar = Salas.objects.create(nome_da_sala='Auditório Principal')

        # Mock para a criação do usuário admin no início
        with patch('usuarios.models.db'):
            # Criamos um admin real no banco de dados de teste
            # para que o gestor possa fazer login no final.
            cls.admin_user = Usuario.create_user(
                nome='Admin Gestor',
                email='admin@ufrpe.br',
                senha='admin_password'
            )

    def setUp(self):
        self.client = Client()

    # Como o fluxo de cadastro e login depende de mocks do Firebase,
    # vamos aplicar os patches a todo o método de teste.
    @patch('usuarios.views.db')
    @patch('usuarios.views.auth_instance')
    @patch('usuarios.views.Usuario.get_by_email') # Mockamos o get_by_email para controlar o retorno
    @patch('usuarios.views.Usuario.create_user') # E o create_user
    def test_professor_registration_and_reservation_flow(self, mock_create_user, mock_get_by_email, mock_auth_instance, mock_db_instance):
        """
        Executa o fluxo completo:
        1. Cadastro de Professor -> 2. Login -> 3. Reserva de Sala -> 4. Logout -> 5. Verificação do Admin
        """

        # --- ETAPA 1: CADASTRO DO PROFESSOR ---
        print("\n--- Iniciando Etapa 1: Cadastro do Professor ---")
        
        # Configuração dos mocks para um cadastro bem-sucedido
        mock_db_instance.collection.return_value.where.return_value.limit.return_value.get.return_value = [] # Email não existe
        mock_auth_instance.create_user_with_email_and_password.return_value = {'localId': 'new-prof-uid'}
        
        # O create_user agora deve criar um usuário REAL no banco de dados de teste
        # para que as outras views possam encontrá-lo.
        # Usamos .side_effect para executar a função real de criação do modelo.
        novo_professor_email = 'professor.novo@ufrpe.br'
        novo_professor_nome = 'Prof. Novo Teste'
        
        # Quando mock_create_user for chamado, ele criará um usuário real no BD de teste.
        # O patch em usuarios.models.db no setUpTestData garante que a chamada ao Firebase dentro do save seja ignorada.
        with patch('usuarios.models.db'):
            mock_create_user.side_effect = lambda nome, email, senha: Usuario.objects.create(nome=nome, email=email)
            
            cadastro_response = self.client.post(reverse('valida_cadastro'), {
                'nome': novo_professor_nome,
                'email': novo_professor_email,
                'senha': 'Password123!'
            })

        # Verificação da Etapa 1
        self.assertRedirects(cadastro_response, '/auth/cadastro/?status=0')
        # Verificamos se o usuário foi realmente criado no banco de dados de teste
        self.assertTrue(Usuario.objects.filter(email=novo_professor_email).exists())
        professor_criado = Usuario.objects.get(email=novo_professor_email)
        print(">>> Sucesso: Professor criado no banco de dados.")

        # --- ETAPA 2: LOGIN DO PROFESSOR ---
        print("\n--- Iniciando Etapa 2: Login do Professor ---")
        
        # Configuração dos mocks para um login bem-sucedido
        mock_auth_instance.sign_in_with_email_and_password.return_value = {'localId': 'new-prof-uid'}
        mock_get_by_email.return_value = professor_criado # Retorna o usuário que acabamos de criar

        login_response = self.client.post(reverse('valida_login'), {
            'email': novo_professor_email,
            'senha': 'Password123!'
        })

        # Verificação da Etapa 2
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.url, reverse('professor:homee'))
        # Verificamos se a sessão foi criada corretamente
        self.assertEqual(self.client.session.get('usuario'), professor_criado.id)
        print(f">>> Sucesso: Login realizado e sessão criada para o usuário ID {professor_criado.id}.")

        # --- ETAPA 3: REALIZAR RESERVA DE SALA ---
        print("\n--- Iniciando Etapa 3: Reserva de Sala ---")
        
        # O cliente agora está "logado" como o professor
        data_reserva_str = (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%dT%H:%M')
        data_devolucao_str = (timezone.now() + timedelta(days=10, hours=2)).strftime('%Y-%m-%dT%H:%M')

        # Desta vez, NÃO mockamos o formulário. Enviamos dados reais.
        reserva_response = self.client.post(reverse('professor:realizar_reserva_salas'), {
            'salas': self.sala_para_reservar.id,
            'usuarios': professor_criado.id,
            'data_reserva': data_reserva_str,
            'data_devolucao': data_devolucao_str
        })

        # Verificação da Etapa 3
        self.assertEqual(reserva_response.status_code, 302)
        self.assertEqual(reserva_response.url, reverse('professor:reserva_sucesso'))
        # A verificação mais importante: a reserva existe no banco de dados?
        self.assertTrue(Reservas.objects.filter(usuarios=professor_criado, salas=self.sala_para_reservar).exists())
        print(f">>> Sucesso: Reserva para a sala '{self.sala_para_reservar.nome_da_sala}' criada.")

        # --- ETAPA 4: LOGOUT DO PROFESSOR ---
        print("\n--- Iniciando Etapa 4: Logout ---")
        
        logout_response = self.client.get(reverse('sair'))
        self.assertRedirects(logout_response, reverse('login'))
        self.assertIsNone(self.client.session.get('usuario'))
        print(">>> Sucesso: Logout realizado e sessão limpa.")

        # --- ETAPA 5: VERIFICAÇÃO DO ADMIN ---
        print("\n--- Iniciando Etapa 5: Verificação do Admin ---")
        
        # Login do admin
        mock_get_by_email.return_value = self.admin_user
        mock_db_instance.collection.return_value.where.return_value.limit.return_value.get.return_value = [MagicMock()]
        
        admin_login_response = self.client.post(reverse('valida_login'), {
            'email': self.admin_user.email,
            'senha': 'admin_password'
        })
        
        self.assertEqual(admin_login_response.url, reverse('gestor:home'))
        
        # Admin acessa uma página que lista as reservas e verifica se a reserva do professor está lá
        # Usaremos a view do calendário de reservas do gestor como exemplo
        admin_view_response = self.client.get(reverse('gestor:calendario_reservas'))
        
        self.assertEqual(admin_view_response.status_code, 200)
        # Verificamos se o nome da sala reservada aparece no HTML da página do gestor
        self.assertContains(admin_view_response, self.sala_para_reservar.nome_da_sala)
        print(f">>> Sucesso: Admin visualizou a reserva do professor na sua tela.")