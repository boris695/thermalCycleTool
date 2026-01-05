# Dockerfile
FROM python:3.11-slim

# Installer les dépendances système
RUN apt-get update && \
    apt-get install -y gcc libfreetype6-dev libpng-dev && \
    pip install --no-cache-dir flask matplotlib numpy

# Créer le dossier de travail
WORKDIR /app

# Copier les fichiers Python et templates
COPY app.py ./
COPY templates ./templates
COPY static ./static

# Exposer le port Flask
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app.py"]