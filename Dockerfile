# Utilisez l'image de base Python
FROM python:3.12.3-bookworm

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Créer un utilisateur non-root pour la sécurité
RUN useradd --create-home --shell /bin/bash app

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiez le fichier requirements.txt dans le conteneur
COPY requirements.txt /app/

# Installez les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste du code source dans le conteneur
COPY . /app/

# Script d'initialisation
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Changer les permissions pour l'utilisateur app
RUN chown -R app:app /app

# Passer à l'utilisateur non-root
USER app

# Exposez le port sur lequel l'application web s'exécute
EXPOSE 8000

# Point d'entrée avec initialisation
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Commande par défaut
CMD ["python", "bpassword/manage.py", "runserver", "0.0.0.0:8000"]