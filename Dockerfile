# Usa uma imagem oficial do Python como base. 'slim' é ótimo para produção.
FROM python:3.11-slim

# Define variáveis de ambiente para o Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Define um diretório de cache para o Matplotlib para evitar erros de permissão
ENV MPLCONFIGDIR=/tmp/matplotlib_cache

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para OpenCV (cv2)
RUN apt-get update && apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências
COPY requirements.txt .

# ETAPA 1: Atualiza o pip separadamente para isolar problemas
RUN python -m pip install --upgrade pip

# ETAPA 2: Instala as dependências com timeout e retries para redes instáveis
RUN python -m pip install --default-timeout=100 --retries=5 --no-cache-dir -r requirements.txt

# Cria um usuário não-root para rodar a aplicação (melhor prática de segurança)
RUN addgroup --system app && adduser --system --group app

# Copia todo o restante do projeto para dentro do container
COPY . .

# Altera o proprietário dos arquivos para o novo usuário
RUN chown -R app:app /app

# Define o usuário que irá rodar os próximos comandos
USER app

# Expõe a porta 8000 para acesso externo
EXPOSE 8000

# Comando para iniciar o servidor Django
# Para produção, troque 'runserver' por um servidor WSGI como Gunicorn:
# CMD ["gunicorn", "seu_projeto.wsgi:application", "--bind", "0.0.0.0:8000"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

