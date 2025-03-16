# Sistema de Mapeamento de Laboratório e Materiais

Este repositório pertence à equipe de PI3 e PI4, composta por:
- **Marcelo Augusto**
- **Marcel Gustavo**
- **Matheus Omar**

## Requisitos
Para executar o projeto em outro computador, é necessário ter o **Python 3** e o **SQLite3** instalados em sua máquina.

## Configuração do Ambiente
Siga os passos abaixo para instalar as dependências e rodar o projeto corretamente.

### 1. Instalação das Dependências
Execute o seguinte comando para instalar todas as dependências necessárias:
```sh
pip install -r requirements.txt
```

### 2. Ativação do Ambiente Virtual
Ative o ambiente virtual para garantir que as dependências sejam utilizadas corretamente:

**No Windows (via PowerShell ou CMD):**
```sh
.\venv\Scripts\Activate
```

**No Linux/macOS:**
```sh
source venv/bin/activate
```

> **Observação:** O comando pode variar dependendo do terminal utilizado.

### 3. Atualização do Banco de Dados
Execute os comandos abaixo para criar e aplicar as migrações no banco de dados:
```sh
python manage.py makemigrations
python manage.py migrate
```

Agora, o projeto está pronto para ser executado!

---

Caso tenha alguma dúvida ou encontre problemas na execução, entre em contato com a equipe.

🚀 **Bom Teste da aplicação! (Email: admin@ufrpe.br e senha: 1234Mg3#d para testar usuário admin cadastrado)**
