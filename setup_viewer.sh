#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si le réseau existe
if ! docker network ls | grep -q hadoop_tp_hadoop_network; then
    print_error "Le réseau 'hadoop_tp_hadoop_network' n'existe pas. Veuillez démarrer l'environnement Hadoop d'abord."
    exit 1
fi

# Créer le dossier templates s'il n'existe pas
mkdir -p templates

# Nettoyer les conteneurs existants
print_message "Nettoyage des conteneurs existants..."
docker stop movie-recommendation-viewer 2>/dev/null || true
docker rm movie-recommendation-viewer 2>/dev/null || true

# Construire l'image Docker
print_message "Construction de l'image Docker..."
if ! docker build -t movie-recommendation-viewer -f Dockerfile.viewer .; then
    print_error "Échec de la construction de l'image Docker"
    exit 1
fi

# Démarrer le conteneur
print_message "Démarrage du conteneur..."
if ! docker run -d \
    --name movie-recommendation-viewer \
    --network hadoop_tp_hadoop_network \
    -p 5000:5000 \
    movie-recommendation-viewer; then
    print_error "Échec du démarrage du conteneur"
    exit 1
fi

# Vérifier que le conteneur est en cours d'exécution
if ! docker ps | grep -q movie-recommendation-viewer; then
    print_error "Le conteneur n'est pas en cours d'exécution"
    docker logs movie-recommendation-viewer
    exit 1
fi

print_message "L'application est accessible à l'adresse : http://localhost:5000"
print_message "Pour voir les logs : docker logs movie-recommendation-viewer"
print_message "Pour arrêter l'application : docker stop movie-recommendation-viewer" 