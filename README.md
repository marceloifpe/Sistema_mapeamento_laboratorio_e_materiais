# Sistema_mapeamento_laboratorio_e_materiais
 Repositório da equipe de PI3 e PI4 composta por: Marcelo Augusto, Marcel Gustavo e Matheus Omar.
Para Excecutar o projeto em outra computador, é só necessário ter o python3 instalado na sua máquina e o sqlite3, segue o passo  a passo de execução de comandos para instalar as dependências e rodar o projeto na sua máquina:
Instalação dos requirements

pip install -r requirements.txt

Ativação do ambiente virtual
*Obs: via shell é esse comando abaixo, dependendo do terminal o comando pode variar.
.\venv\Scripts\Activate

Atualização do banco de dados

python manage.py makemigrations
python manage.py migrate