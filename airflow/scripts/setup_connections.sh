#!/bin/bash

# Attendre que Airflow soit prêt
until curl -s http://localhost:8080/health | grep -q "healthy"; do
    echo "Waiting for Airflow to be ready..."
    sleep 5
done

# Créer la connexion Spark
airflow connections add 'spark_default' \
    --conn-type 'spark' \
    --conn-host 'spark://spark-master:7077' \
    --conn-extra '{"queue": "default", "deploy-mode": "cluster"}' 