#!/usr/bin/env bash
set -euo pipefail

# On force psql à utiliser POSTGRES_USER/POSTGRES_PASSWORD
export PGPASSWORD="${POSTGRES_PASSWORD}"
PSQL="psql -v ON_ERROR_STOP=1 -U \"${POSTGRES_USER}\""

# Vérifier l'existence d'une DB
database_exists() {
  $PSQL -tAc "SELECT 1 FROM pg_database WHERE datname = '$1'" | grep -q 1
}

# Vérifier l'existence d'un rôle
user_exists() {
  $PSQL -tAc "SELECT 1 FROM pg_roles WHERE rolname = '$1'" | grep -q 1
}

# 1) Base metastore + user hive
if ! database_exists metastore; then
  echo "=> Création de la base metastore..."
  $PSQL -c "CREATE DATABASE metastore;"
fi

if ! user_exists hive; then
  echo "=> Création du rôle hive..."
  $PSQL -c "CREATE USER hive WITH PASSWORD 'hive';"
  $PSQL -c "GRANT ALL PRIVILEGES ON DATABASE metastore TO hive;"
fi

echo "=> Import du schéma Hive dans metastore..."
$PSQL -d metastore -f /hive-schema-3.1.0.postgres.sql

# 2) Base airflow + user airflow
if ! database_exists airflow; then
  echo "=> Création de la base airflow..."
  $PSQL -c "CREATE DATABASE airflow;"
fi

if ! user_exists airflow; then
  echo "=> Création du rôle airflow..."
  $PSQL -c "CREATE USER airflow WITH PASSWORD 'airflow';"
  $PSQL -c "GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;"
fi

echo "✅ init-databases.sh terminé." 