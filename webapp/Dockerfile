# ============================================================================
# Dockerfile de la app web (Flask)
# ============================================================================


# --- FROM: punto de partida -------------------------------------------------
# Toda imagen parte de otra imagen base. Aquí se parte de una que ya trae
# Python 3.12 instalado, así no hace falta instalarlo a mano.
# "slim" es una versión recortada y liviana (menos cosas = imagen más pequeña).
FROM python:3.12-slim


# --- ENV: variables de entorno ----------------------------------------------
# Define ajustes que estarán disponibles dentro del contenedor.
#   PYTHONDONTWRITEBYTECODE=1 -> evita que Python genere archivos .pyc (cache
#                               que no se necesita dentro del contenedor).
#   PYTHONUNBUFFERED=1        -> hace que los mensajes (print/logs) salgan al
#                               instante, sin quedarse en un buffer. Útil para
#                               ver los logs en tiempo real.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


# --- WORKDIR: carpeta de trabajo --------------------------------------------
# Crea (si no existe) la carpeta /app DENTRO del contenedor y se posiciona en
# ella. A partir de aquí, los comandos siguientes se ejecutan desde /app.
# Es como hacer "cd /app", pero dentro de la imagen.
WORKDIR /app


# --- COPY + RUN: instalar dependencias --------------------------------------
# Se copia SOLO el archivo de dependencias primero (requirements.txt).
# ¿Por qué solo ese y no todo el proyecto todavía? Por eficiencia: Docker
# guarda en cache cada paso. Si el código cambia pero las dependencias no,
# Docker reutiliza la instalación ya hecha y la construcción es mucho más rápida.
COPY requirements.txt .

# RUN ejecuta un comando mientras se CONSTRUYE la imagen (una sola vez).
# Aquí pip lee requirements.txt e instala las librerías (Flask, etc.).
#   --no-cache-dir -> no guarda la cache de pip, para que la imagen pese menos.
RUN pip install --no-cache-dir -r requirements.txt


# --- COPY: copiar el resto del código ---------------------------------------
# Ahora sí se copia todo lo demás del proyecto (app.py, templates, etc.)
# desde el equipo hacia la carpeta /app del contenedor.
# El primer "." = carpeta actual en el equipo (donde está este Dockerfile).
# El segundo "." = carpeta actual dentro del contenedor (/app por el WORKDIR).
COPY . .


# --- EXPOSE: documentar el puerto -------------------------------------------
# Indica que la app escucha en el puerto 5000 dentro del contenedor.
# Es informativo: por sí solo NO abre el puerto hacia afuera. La publicación
# real del puerto se hace al ejecutar (en el docker-compose.yml con "ports").
EXPOSE 5000


# --- CMD: qué comando corre cuando arranca el contenedor --------------------
# Mientras FROM/COPY/RUN se ejecutan al CONSTRUIR la imagen, CMD se ejecuta al
# ARRANCAR el contenedor. Es el programa principal.
# Aquí se lanza gunicorn, un servidor que pone en marcha la app Flask.
#   --bind 0.0.0.0:5000 -> escucha en el puerto 5000 en todas las direcciones
#                          (0.0.0.0) para que sea accesible desde fuera.
#   --workers 2         -> 2 procesos atendiendo peticiones a la vez.
#   app:app             -> en el archivo app.py, usa la variable llamada 'app'
#                          (el formato es "archivo:variable", sin el .py).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
