#!/bin/bash

# Export JAVA_HOME pour tous les scripts Hadoop
export JAVA_HOME=/usr/local/openjdk-11
export PATH=$PATH:$JAVA_HOME/bin

# Vérification de JAVA_HOME
if [ -z "$JAVA_HOME" ]; then
    echo "ERROR: JAVA_HOME is not set"
    exit 1
fi

# Vérification que Java est accessible
if ! command -v java &> /dev/null; then
    echo "ERROR: Java is not accessible"
    exit 1
fi

# Démarrage du service SSH
service ssh start

set -e

# Fonction pour formater le namenode
format_namenode() {
    echo "Formatting namenode..."
    echo "Y" | hdfs namenode -format
}

# Fonction pour démarrer HDFS
start_hdfs() {
    echo "Starting HDFS services..."
    start-dfs.sh
}

# Fonction pour démarrer YARN
start_yarn() {
    echo "Starting YARN services..."
    start-yarn.sh
}

# Fonction pour vérifier le statut des services
check_status() {
    echo "Checking HDFS status..."
    hdfs dfsadmin -report
    
    echo "Checking YARN status..."
    yarn node -list
}

# Exécution des fonctions selon le rôle du conteneur
case "$(hostname)" in
    "namenode")
        format_namenode
        start_hdfs
        check_status
        ;;
    "resourcemanager")
        start_yarn
        check_status
        ;;
    "datanode"*)
        echo "Starting datanode services..."
        hdfs datanode
        ;;
esac

# Garder le conteneur en vie
tail -f /dev/null 