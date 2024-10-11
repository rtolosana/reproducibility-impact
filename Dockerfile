# Usa una imagen de Python como base
FROM python:3.9

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias
RUN pip install scholarly'[tor]'

COPY code/get-citations.py /app/get-citations.py

CMD ["python", "get-citations.py"]
