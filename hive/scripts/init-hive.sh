#!/bin/bash

# Configuration des variables d'environnement
export HADOOP_HOME=/opt/hadoop
export HIVE_HOME=/opt/hive
export PATH=$PATH:$HIVE_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Configuration Java
export JAVA_HOME=/usr/local/openjdk-11
export PATH=$PATH:$JAVA_HOME/bin

# Configuration HDFS
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root

# Configuration YARN
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root

# Création des répertoires nécessaires
mkdir -p $HIVE_HOME/logs
mkdir -p /tmp/hive

# Attendre que PostgreSQL soit prêt
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h postgres -p 5432 -U postgres; do
    sleep 1
done

# Initialiser le schéma Hive
echo "Initializing Hive schema..."
schematool -dbType postgres -initSchema

# Démarrer le metastore Hive
echo "Starting Hive metastore..."
hive --service metastore &

# Démarrer le serveur Hive
echo "Starting Hive server..."
hive --service hiveserver2 &

# Garder le conteneur en vie
tail -f /dev/null 