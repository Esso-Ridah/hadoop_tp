#!/bin/bash

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    print_message "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier les permissions Docker
    if ! docker info &> /dev/null; then
        print_error "Vous n'avez pas les permissions pour exécuter Docker. Ajoutez votre utilisateur au groupe docker."
        exit 1
    fi
}

# Création des répertoires nécessaires
create_directories() {
    print_message "Création des répertoires nécessaires..."
    
    # Créer les répertoires pour les données persistantes
    mkdir -p data/namenode
    mkdir -p data/datanode1
    mkdir -p data/datanode2
    mkdir -p data/datanode3
    mkdir -p data/postgres
    mkdir -p data/spark
    
    # Créer les répertoires pour Airflow
    mkdir -p airflow/dags
    mkdir -p airflow/logs
    mkdir -p airflow/plugins
}

# Configuration des permissions
setup_permissions() {
    print_message "Configuration des permissions..."
    
    # Donner les permissions nécessaires aux répertoires
    chmod -R 777 data/
    chmod -R 777 airflow/
    
    # Définir l'UID Airflow
    export AIRFLOW_UID=$(id -u)
}

# Construction et démarrage des conteneurs
start_containers() {
    print_message "Construction et démarrage des conteneurs..."
    
    # Arrêter les conteneurs existants et supprimer les volumes
    docker-compose down -v
    
    # Supprimer les données existantes
    sudo rm -rf data/postgres/*
    
    # Démarrer d'abord PostgreSQL
    docker-compose up -d postgres
    
    # Attendre que PostgreSQL soit prêt
    print_message "Attente du démarrage de PostgreSQL..."
    sleep 30
    
    # Démarrer les autres services
    docker-compose up -d
}

# Initialisation d'Airflow
setup_airflow() {
    print_message "Initialisation d'Airflow..."
    
    # Attendre que les services soient prêts
    sleep 30
    
    # Initialiser la base de données
    docker exec -it airflow-webserver airflow db migrate
    
    # Créer l'utilisateur admin
    docker exec -it airflow-webserver airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin
}

# Test des connexions
test_connections() {
    print_message "Test des connexions..."
    
    # Test de la connexion à HDFS
    print_message "Test de la connexion à HDFS..."
    docker exec -it namenode hdfs dfs -ls /
    
    # Test de la connexion à YARN
    print_message "Test de la connexion à YARN..."
    docker exec -it resourcemanager yarn node -list
    
    # Test de la connexion à Spark
    print_message "Test de la connexion à Spark..."
    docker exec -it spark-master spark-sql -e "SHOW DATABASES;"
}

# Test du DAG MovieLens
test_movielens_dag() {
    print_message "Test du DAG MovieLens..."
    
    # Attendre que Airflow soit complètement démarré
    sleep 30
    
    # Copier le DAG MovieLens
    print_message "Copie du DAG MovieLens..."
    cp movielens_ingestion.py airflow/dags/
    
    # Attendre que le DAG soit détecté
    print_message "Attente de la détection du DAG..."
    sleep 30
    
    # Déclencher le DAG
    print_message "Déclenchement du DAG MovieLens..."
    docker exec -it airflow-webserver airflow dags trigger movielens_ingestion
    
    print_message "Le DAG MovieLens a été déclenché. Vérifiez l'interface Airflow pour suivre son exécution."
}

# Fonction principale
main() {
    check_prerequisites
    create_directories
    setup_permissions
    start_containers
    setup_airflow
    test_connections
    test_movielens_dag
    
    print_message "Installation terminée avec succès !"
    print_message "Interfaces web disponibles :"
    print_message "- HDFS NameNode : http://localhost:9870"
    print_message "- YARN ResourceManager : http://localhost:8088"
    print_message "- Spark Master : http://localhost:8080"
    print_message "- Airflow : http://localhost:8081 (utilisateur: admin, mot de passe: admin)"
    print_message ""
    print_message "Le DAG MovieLens a été déclenché. Vérifiez l'interface Airflow pour suivre son exécution."
}

# Exécution du script
main 