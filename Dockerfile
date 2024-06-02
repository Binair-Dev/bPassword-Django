# Utilisez l'image de base Python
FROM python:3.12.3-bookworm

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le fichier requirements.txt dans le conteneur
COPY requirements.txt /app/

# Installez les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste du code source dans le conteneur
COPY . /app/

# Exposez le port sur lequel l'application web s'exécute
EXPOSE 8000

# Commande pour démarrer l'application Django
CMD ["python", "bpassword/manage.py", "runserver", "0.0.0.0:8000"]