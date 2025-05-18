#!/bin/bash

# Attendre que le metastore soit prêt
until nc -z hive-metastore 9083
do
  echo "Waiting for hive-metastore..."
  sleep 2
done

# Démarrer le serveur Hive
hive --service hiveserver2 