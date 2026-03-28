# Usa o Python 3.11 limpo e leve
FROM python:3.11-slim

# Cria a pasta do app lá dentro
WORKDIR /app

# Instala as dependências primeiro (aproveita o cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do seu código
COPY . .

# Comando para subir a API exposta para o mundo externo do container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
