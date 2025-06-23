from django.test import TestCase, Client
from django.urls import reverse

class MateriaisViewsTestCase(TestCase):
    """
    Suite de testes para as views do app 'materiais'.
    """

    def setUp(self):
        """
        Configuração executada antes de cada teste.
        Aqui, criamos uma instância do cliente de teste.
        """
        self.client = Client()

    def test_home_view_retorna_sucesso_e_conteudo_correto(self):
        """
        Testa se a view 'home' do app 'materiais' funciona como esperado.
        """
        # 1. Obter a URL para a view 'home' usando seu nome 'materiais:home'
        url = reverse('materiais:home')

        # 2. Fazer uma requisição GET para a URL obtida
        response = self.client.get(url)

        # 3. Verificar se a resposta tem o status code 200 (OK)
        self.assertEqual(response.status_code, 200)

        # 4. Verificar se o conteúdo da resposta é exatamente 'Olá'
        # Usamos .decode() para converter a resposta (que vem em bytes) para uma string.
        self.assertEqual(response.content.decode('utf-8'), 'Olá')