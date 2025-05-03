# Usa uma imagem oficial do Python como base
FROM python:3.11-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro
COPY requirements.txt .

# Instala as dependências
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do projeto para dentro do container
COPY . .

# Expõe a porta 8000 para acesso externo
EXPOSE 8000

# Comando para iniciar o servidor Django dentro do container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
