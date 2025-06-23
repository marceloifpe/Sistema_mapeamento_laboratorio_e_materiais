# Usa uma imagem oficial do Python como base. 'slim' é ótimo para produção.
FROM python:3.11-slim

# Define variáveis de ambiente para o Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MPLCONFIGDIR=/tmp/matplotlib_cache

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala as dependências de sistema essenciais e completas para OpenCV e streaming de vídeo
# Esta lista combina as nossas descobertas com as sugestões da sua análise.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dependências gráficas básicas
    libgl1-mesa-glx \
    libglib2.0-0 \
    # libsm6 \
    # libxext6 \
    # libxrender1 \
    # libgtk-3-0 \
    # libgomp1 \
    # # Dependências de Vídeo (V4L2 - Crucial para a câmara)
    # libv4l-dev \
    # v4l-utils \
    # # Dependências de Codecs (FFmpeg - Backend robusto para o OpenCV)
    # libavcodec-dev \
    # libavformat-dev \
    # libswscale-dev \
    # libxvidcore-dev \
    # libx264-dev \
    # # Dependências de Imagem
    # libjpeg-dev \
    # libpng-dev \
    # libtiff-dev \
    # # Outras dependências úteis
    # libdc1394-dev \
    # libtbb-dev \
    # pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências
COPY requirements.txt .

# Atualiza o pip e instala as bibliotecas Python
RUN python -m pip install --upgrade pip && \
    python -m pip install --default-timeout=100 --retries=5 --no-cache-dir -r requirements.txt

# Cria um usuário não-root para rodar a aplicação
RUN addgroup --system app && adduser --system --group app

# Adiciona o utilizador 'app' ao grupo 'video' para acesso à câmara
# RUN usermod -aG video app

# Copia todo o restante do projeto para dentro do container
COPY . .

# --------------------------------------------------------------------
# >>> ETAPA DE VALIDAÇÃO ADICIONADA AQUI <<<
# Executa a suíte de testes completa do projeto. Se qualquer teste
# falhar, o build do Docker será interrompido neste ponto.
# --------------------------------------------------------------------
RUN python manage.py test

# Altera o proprietário dos arquivos para o novo usuário
RUN chown -R app:app /app

# Define o usuário que irá rodar os próximos comandos
USER app

# Expõe a porta 8000
EXPOSE 8000

# Comando para iniciar o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]