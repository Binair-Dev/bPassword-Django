#!/bin/bash

# 🚀 Script de déploiement simple - PRÉSERVE LES DONNÉES
# Ce script redéploie l'application sans perdre la base de données

echo "🔄 Déploiement bPassword - Mode sécurisé (préservation des données)"

# Créer les dossiers persistants s'ils n'existent pas
mkdir -p data
mkdir -p backups
mkdir -p logs

echo "📁 Dossiers de données créés/vérifiés"

# Arrêter les services (SANS supprimer les volumes)
echo "⏹️  Arrêt des services..."
docker-compose -f docker-compose.simple.yml stop

# Nettoyer les images obsolètes
echo "🧹 Nettoyage des images obsolètes..."
docker system prune -f

# Rebuild l'image
echo "🔨 Reconstruction de l'image..."
docker-compose -f docker-compose.simple.yml build --no-cache

# Relancer les services
echo "🚀 Redémarrage des services..."
docker-compose -f docker-compose.simple.yml up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage..."
sleep 10

# Vérifier le statut
echo "✅ Vérification du statut..."
docker-compose -f docker-compose.simple.yml ps

echo ""
echo "🎉 Déploiement terminé !"
echo "📊 Application disponible sur : http://localhost:8001"
echo "💾 Base de données persistante dans : ./data/"
echo "📋 Logs disponibles dans : ./logs/"
echo ""
echo "📝 Pour voir les logs en temps réel :"
echo "   docker-compose -f docker-compose.simple.yml logs -f web"