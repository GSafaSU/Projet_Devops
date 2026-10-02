# Image de base : une Debian minimale avec Python 3.12 déjà installé
FROM python:3.12-slim

# Les logs de Python partent immédiatement, sans mise en tampon
ENV PYTHONNUNBUFFERED=1

# Un utilisateur sans privilèges, pour ne pas faire tourner l'API en root
RUN useradd --create-home appuser

# Le dossier de travail à l'intérieur de l'image
WORKDIR /app

# D'abord les dépendances (elles changent rarement : mises en cache)
COPY app/requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt

# Ensuite le code (il change souvent)
COPY app/ .

# À partir d'ici, tout s'exécute en tant que appuser
USER appuser

# Documentation : l'API écoute sur le port 8000
EXPOSE 8000

# La commande lancée au démarrage de chaque conteneur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]