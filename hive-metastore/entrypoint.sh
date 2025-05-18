#!/bin/bash
set -e

# Attendre que PostgreSQL soit prêt
/wait-for-it.sh postgres:5432 -t 60

# Initialiser le schéma Hive
schematool -initSchema -dbType postgres

# Démarrer le metastore Hive
hive --service metastore 