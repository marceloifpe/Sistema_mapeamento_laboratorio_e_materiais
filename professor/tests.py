from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

# Importando os modelos de outros apps
from usuarios.models import Usuario
from salas.models import Salas, Reservas
from materiais.models import Materiais, Reserva

class ProfessorViewsTestCase(TestCase):
    """
    Suite de testes para as views do app 'professor'.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Configura os dados iniciais que serão usados em todos os testes.
        Isso é executado apenas uma vez para a classe toda.
        """
        # Mock para evitar chamadas reais ao Firebase durante a criação de usuários
        with patch('usuarios.models.db') as mock_firebase_db:
            mock_firebase_db.collection.return_value.document.return_value.set.return_value = None
            cls.user = Usuario.create_user(
                nome='Professor Teste',
                email='professor@teste.com',
                senha='password123'
            )

        # Criar objetos para simular reservas
        cls.sala = Salas.objects.create(nome_da_sala='Sala de Teste 101')
        cls.material = Materiais.objects.create(nome_do_material='Projetor de Teste')

        # Criar uma reserva de sala e uma de material para o nosso usuário de teste
        # Usamos datas futuras para passar em qualquer validação de "não reservar no passado"
        data_reserva = timezone.now() + timedelta(days=5)
        data_devolucao = data_reserva + timedelta(hours=3)

        cls.reserva_sala = Reservas.objects.create(
            salas=cls.sala,
            usuarios=cls.user,
            data_reserva=data_reserva,
            data_devolucao=data_devolucao
        )
        cls.reserva_material = Reserva.objects.create(
            materiais=cls.material,
            usuarios=cls.user,
            data_reserva=data_reserva,
            data_devolucao=data_devolucao
        )

    def setUp(self):
        """
        Configuração executada antes de cada teste individual.
        """
        self.client = Client()
        # Simular o login do usuário colocando seu ID na sessão
        session = self.client.session
        session['usuario'] = self.user.id
        session.save()

    def test_homee_view_para_usuario_logado(self):
        """ Testa se a view homee carrega corretamente para um usuário autenticado. """
        response = self.client.get(reverse('professor:homee'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homee.html')
        # Verifica se as reservas do usuário estão no contexto da página
        self.assertIn('ReservasSalas', response.context)
        self.assertIn('ReservasMateriais', response.context)
        self.assertEqual(list(response.context['ReservasSalas']), [self.reserva_sala])

    def test_homee_view_redireciona_se_nao_logado(self):
        """ Testa se a view homee redireciona para o login se o usuário não estiver autenticado. """
        client_nao_logado = Client() # Um novo cliente sem sessão de usuário
        response = client_nao_logado.get(reverse('professor:homee'))
        self.assertEqual(response.status_code, 302) # 302 é o código para redirecionamento
        self.assertRedirects(response, '/auth/login/?status=2')

    def test_ver_salas_professor_view(self):
        """ Testa se um professor pode ver os detalhes de sua própria reserva de sala. """
        response = self.client.get(reverse('professor:ver_salas_professor', kwargs={'id': self.reserva_sala.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ver_salas_professor.html')
        self.assertContains(response, self.sala.nome_da_sala)

    def test_ver_materiais_professor_view(self):
        """ Testa se um professor pode ver os detalhes de sua própria reserva de material. """
        response = self.client.get(reverse('professor:ver_materiais_professor', kwargs={'id': self.reserva_material.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ver_materiais_professor.html')
        self.assertContains(response, self.material.nome_do_material)

    @patch('professor.views.RealizarReservas')
    def test_realizar_reserva_salas_com_sucesso(self, mock_form_sala):
        """ Testa o POST para criar uma reserva de sala com dados válidos (usando mock). """
        # Configuramos o mock para simular um formulário válido
        mock_form_sala.return_value.is_valid.return_value = True

        response = self.client.post(reverse('professor:realizar_reserva_salas'), data={'key': 'value'})
        
        # Verifica se redirecionou para a página de sucesso
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('professor:reserva_sucesso'))
        # Verifica se o método save() do formulário foi chamado
        mock_form_sala.return_value.save.assert_called_once()

    @patch('professor.views.RealizarReservas')
    def test_realizar_reserva_salas_com_dados_invalidos(self, mock_form_sala):
        """ Testa o POST para criar uma reserva de sala com dados inválidos (usando mock). """
        # Configuramos o mock para simular um formulário inválido
        mock_form_sala.return_value.is_valid.return_value = False

        response = self.client.post(reverse('professor:realizar_reserva_salas'), data={'key': 'value'})

        # Verifica se redirecionou para a página de dados inválidos
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('professor:reserva_dados_invalidos'))
        # Verifica se o método save() do formulário NÃO foi chamado
        mock_form_sala.return_value.save.assert_not_called()

    @patch('professor.views.RealizarReserva')
    def test_realizar_reserva_materiais_com_sucesso(self, mock_form_material):
        """ Testa o POST para criar uma reserva de material com dados válidos (usando mock). """
        mock_form_material.return_value.is_valid.return_value = True
        response = self.client.post(reverse('professor:realizar_reserva_materiais'), data={'key': 'value'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('professor:reserva_sucesso'))
        mock_form_material.return_value.save.assert_called_once()
        
    def test_reserva_sucesso_view(self):
        """ Testa se a página de sucesso de reserva carrega. """
        response = self.client.get(reverse('professor:reserva_sucesso'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reserva_sucesso.html')