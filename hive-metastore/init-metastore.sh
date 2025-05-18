#!/bin/bash

# Attendre que PostgreSQL soit prêt
until pg_isready -h postgres -p 5432 -U hive
do
  echo "Waiting for postgres..."
  sleep 2
done

# Initialiser le schéma Hive
schematool -initSchema -dbType postgres

# Démarrer le metastore
hive --service metastore 