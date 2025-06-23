from django.test import TestCase, Client
from django.urls import reverse

class SalasViewsTestCase(TestCase):
    """
    Suite de testes para as views do app 'salas'.
    """

    def setUp(self):
        """
        Configura o ambiente para cada teste, criando um cliente de teste.
        """
        self.client = Client()

    def test_home_view_sala(self):
        """
        Testa se a view 'home' do app 'salas' retorna
        o status code 200 e o conteúdo esperado.
        """
        # 1. Obtém a URL da view 'home' usando o namespace 'salas'
        url = reverse('salas:home')

        # 2. Simula uma requisição GET para essa URL
        response = self.client.get(url)

        # 3. Verifica se a página carregou com sucesso (status 200)
        self.assertEqual(response.status_code, 200)

        # 4. Verifica se o conteúdo retornado é exatamente 'Olá'
        self.assertEqual(response.content.decode('utf-8'), 'Olá')