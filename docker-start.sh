#!/bin/bash

# Script de démarrage Docker pour bPassword Django
set -e

echo "🐳 Script de démarrage Docker bPassword"
echo "======================================="

# Fonction d'aide
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  dev        Démarrer en mode développement (SQLite)"
    echo "  prod       Démarrer en mode production (PostgreSQL + Nginx)"
    echo "  simple     Démarrer en mode simple (SQLite, sans PostgreSQL)"
    echo "  build      Construire les images Docker"
    echo "  stop       Arrêter tous les services"
    echo "  logs       Afficher les logs"
    echo "  backup     Effectuer une sauvegarde"
    echo "  shell      Ouvrir un shell dans le conteneur web"
    echo "  clean      Nettoyer les volumes et images"
    echo "  help       Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 dev     # Démarrage rapide pour le développement"
    echo "  $0 simple  # Démarrage simple sans PostgreSQL"
    echo "  $0 prod    # Démarrage production complète"
    echo "  $0 backup  # Sauvegarder les données"
}

# Vérifier Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker n'est pas installé!"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ docker-compose n'est pas installé!"
        exit 1
    fi
}

# Mode développement
start_dev() {
    echo "🚀 Démarrage en mode développement..."
    docker-compose -f docker-compose.dev.yml up --build -d
    echo ""
    echo "✅ bPassword démarré en mode développement!"
    echo "📱 Interface: http://localhost:8000"
    echo "👨‍💼 Admin: http://localhost:8000/admin (admin/admin123)"
    echo ""
    echo "Pour voir les logs: docker-compose -f docker-compose.dev.yml logs -f"
}

# Mode simple (SQLite, sans PostgreSQL)
start_simple() {
    echo "🚀 Démarrage en mode simple (SQLite uniquement)..."
    docker-compose -f docker-compose.simple.yml up --build -d
    echo ""
    echo "✅ bPassword démarré en mode simple!"
    echo "📱 Interface: http://localhost:8150"
    echo "👨‍💼 Admin: http://localhost:8150/admin (admin/admin123)"
    echo "🗄️  Base de données: SQLite"
    echo ""
    echo "Pour voir les logs: docker-compose -f docker-compose.simple.yml logs -f"
}

# Mode production
start_prod() {
    echo "🏭 Démarrage en mode production..."
    
    # Vérifier les variables d'environnement
    if [ ! -f .env ]; then
        echo "⚠️  Fichier .env manquant, création depuis le template..."
        cp .env.example .env
        echo "📝 Veuillez configurer le fichier .env avant de continuer."
        exit 1
    fi
    
    docker-compose up --build -d web
    echo ""
    echo "✅ bPassword démarré en mode production!"
    echo "📱 Interface: http://localhost:8150"
    echo "🗄️  Base de données: SQLite (par défaut)"
    echo ""
    echo "Pour PostgreSQL: décommenter DATABASE_URL dans docker-compose.yml et redémarrer"
    echo "Pour activer Nginx: docker-compose --profile production up nginx -d"
}

# Construire les images
build_images() {
    echo "🔨 Construction des images Docker..."
    docker-compose build --no-cache
    echo "✅ Images construites!"
}

# Arrêter les services
stop_services() {
    echo "⏹️  Arrêt des services..."
    docker-compose -f docker-compose.yml down
    docker-compose -f docker-compose.dev.yml down
    echo "✅ Services arrêtés!"
}

# Afficher les logs
show_logs() {
    echo "📄 Logs des services..."
    if docker-compose ps | grep -q "bpassword_dev"; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose logs -f
    fi
}

# Sauvegarde
run_backup() {
    echo "💾 Démarrage de la sauvegarde..."
    docker-compose --profile backup run --rm backup /backup.sh
    echo "✅ Sauvegarde terminée!"
}

# Shell dans le conteneur
open_shell() {
    echo "🐚 Ouverture du shell..."
    if docker-compose ps | grep -q "bpassword_dev"; then
        docker-compose -f docker-compose.dev.yml exec web bash
    else
        docker-compose exec web bash
    fi
}

# Nettoyage
clean_all() {
    echo "🧹 Nettoyage des volumes et images..."
    read -p "⚠️  Êtes-vous sûr de vouloir supprimer tous les volumes ? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        docker-compose -f docker-compose.dev.yml down -v
        docker system prune -f
        docker volume prune -f
        echo "✅ Nettoyage terminé!"
    else
        echo "❌ Nettoyage annulé."
    fi
}

# Script principal
main() {
    check_docker
    
    case "${1:-help}" in
        "dev")
            start_dev
            ;;
        "simple")
            start_simple
            ;;
        "prod")
            start_prod
            ;;
        "build")
            build_images
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            show_logs
            ;;
        "backup")
            run_backup
            ;;
        "shell")
            open_shell
            ;;
        "clean")
            clean_all
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

main "$@"