import base64
from io import BytesIO
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# Importando os modelos dos seus respectivos apps
from usuarios.models import Usuario
from salas.models import Salas, Reservas
from materiais.models import Materiais, Reserva

# --- ALTERAÇÃO AQUI: Importações necessárias para criar a imagem falsa ---
from PIL import Image

# Silencia o warning do Matplotlib
import matplotlib
matplotlib.use('Agg')

class GestorViewsTestCase(TestCase):
    """
    Suite de testes para as views do app 'gestor'.
    """

    @classmethod
    def setUpTestData(cls):
        with patch('usuarios.models.db') as mock_firebase_db:
            mock_firebase_db.collection.return_value.document.return_value.set.return_value = None
            cls.user = Usuario.create_user(
                nome='Usuário de Teste',
                email='test@example.com',
                senha='password123'
            )
            cls.admin_user = Usuario.create_user(
                nome='Admin UFRPE',
                email='admin@ufrpe.br',
                senha='password123'
            )

        cls.sala1 = Salas.objects.create(nome_da_sala='Laboratório de Redes')
        cls.sala2 = Salas.objects.create(nome_da_sala='Auditório Principal')

        cls.material1 = Materiais.objects.create(nome_do_material='Projetor Epson')
        cls.material2 = Materiais.objects.create(nome_do_material='Protoboard')

        future_date_ref = timezone.now() + timedelta(days=365) # 1 ano no futuro

        data_2026 = future_date_ref.replace(year=2026)
        Reservas.objects.create(salas=cls.sala1, usuarios=cls.user, data_reserva=data_2026.replace(month=5, day=10), data_devolucao=data_2026.replace(month=5, day=10) + timedelta(hours=2))
        Reservas.objects.create(salas=cls.sala1, usuarios=cls.user, data_reserva=data_2026.replace(month=5, day=15), data_devolucao=data_2026.replace(month=5, day=15) + timedelta(hours=2))
        Reservas.objects.create(salas=cls.sala2, usuarios=cls.user, data_reserva=data_2026.replace(month=6, day=20), data_devolucao=data_2026.replace(month=6, day=20) + timedelta(hours=2))

        data_2027 = future_date_ref.replace(year=2027)
        Reserva.objects.create(materiais=cls.material1, usuarios=cls.user, data_reserva=data_2026.replace(month=7, day=1), data_devolucao=data_2026.replace(month=7, day=1) + timedelta(days=1))
        Reserva.objects.create(materiais=cls.material1, usuarios=cls.user, data_reserva=data_2026.replace(month=8, day=1), data_devolucao=data_2026.replace(month=8, day=1) + timedelta(days=1))
        Reserva.objects.create(materiais=cls.material1, usuarios=cls.user, data_reserva=data_2026.replace(month=9, day=1), data_devolucao=data_2026.replace(month=9, day=1) + timedelta(days=1))
        Reserva.objects.create(materiais=cls.material2, usuarios=cls.user, data_reserva=data_2027.replace(month=12, day=5), data_devolucao=data_2027.replace(month=12, day=5) + timedelta(days=1))


    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['usuario'] = self.user.id
        session.save()

    def test_ranking_salas_view_loads_correctly(self):
        response = self.client.get(reverse('gestor:ranking_salas'))
        self.assertEqual(response.status_code, 200)

    def test_ranking_salas_view_with_filter(self):
        response = self.client.get(reverse('gestor:ranking_salas') + '?ano=2026&mes=5')
        self.assertEqual(response.status_code, 200)

    def test_ranking_materiais_view_loads_correctly(self):
        response = self.client.get(reverse('gestor:ranking_materiais'))
        self.assertEqual(response.status_code, 200)

    def test_ranking_materiais_view_with_filter(self):
        response = self.client.get(reverse('gestor:ranking_materiais') + '?ano=2027')
        self.assertEqual(response.status_code, 200)

    @patch('gestor.views.get_firebase_users')
    def test_usuario_list_view_without_firebase(self, mock_get_firebase_users):
        mock_get_firebase_users.return_value = [
            {'id': 'firebase_id_1', 'nome': 'Firebase User 1', 'email': 'fb1@example.com'},
        ]
        response = self.client.get(reverse('gestor:usuarios_cadastrados'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios_cadastrados.html')
        
    def test_cadastrar_material_camera_web_get_request(self):
        response = self.client.get(reverse('gestor:cadastrar_material_camera_web'))
        self.assertEqual(response.status_code, 200)

    # --- ALTERAÇÃO FINAL AQUI ---
    @patch('gestor.views.reconhecer_material_yolo')
    @patch('gestor.views.base64.b64decode')
    def test_video_feed_material_detectado(self, mock_b64decode, mock_reconhecer_material):
        """
        Testa o endpoint de vídeo. Agora, cria uma imagem 1x1 válida em memória
        para que a biblioteca Pillow não dê erro ao processá-la.
        """
        # 1. Criar os bytes de uma imagem 1x1 PNG válida
        buffer = BytesIO()
        Image.new('RGB', (1, 1)).save(buffer, format='PNG')
        fake_image_bytes = buffer.getvalue()

        # 2. Configurar os mocks
        mock_reconhecer_material.return_value = 'protoboard'
        mock_b64decode.return_value = fake_image_bytes # Agora retorna bytes de uma imagem real

        # 3. Executar o teste
        dummy_image_data = "data:image/jpeg;base64,SGVsbG8sIFdvcmxkIQ=="
        response = self.client.post(reverse('gestor:video_feed'), {'image_data': dummy_image_data})

        # 4. Verificar o resultado
        self.assertEqual(response.status_code, 200)
        mock_reconhecer_material.assert_called_once()
        mock_b64decode.assert_called_once()
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'status': 'detectado', 'material': 'protoboard'}
        )