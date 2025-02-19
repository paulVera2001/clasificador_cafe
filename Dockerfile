FROM python:3.9-slim

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y wget xz-utils
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb
RUN apt-get install -y ./wkhtmltox_0.12.6-1.bionic_amd64.deb
RUN rm -f wkhtmltox_0.12.6-1.bionic_amd64.deb

# Crea el entorno de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . /app

# Instala dependencias de Python
RUN pip install -r requirements.txt

# Exponer el puerto de tu aplicación Flask
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]
