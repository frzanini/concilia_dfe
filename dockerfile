# Base image
FROM python:3.12.7-slim

# Diretório de trabalho
WORKDIR /app

COPY . .
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install streamlit pandas openpyxl

COPY src/ ./src/

EXPOSE 8501
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.enableCORS=false"]



