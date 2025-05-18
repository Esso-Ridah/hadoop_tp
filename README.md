# Environnement Hadoop avec Spark et Airflow

Ce projet met en place un environnement de développement Hadoop complet avec Spark pour le traitement de données et Airflow pour l'orchestration des tâches.

## Composants

- **Hadoop HDFS** : Stockage distribué
  - 1 NameNode
  - 3 DataNodes
- **Hadoop YARN** : Gestion des ressources
  - 1 ResourceManager
  - 3 NodeManagers
- **Apache Spark** : Moteur de traitement de données
  - 1 Spark Master
  - 2 Spark Workers
- **Apache Airflow** : Orchestration des tâches
  - 1 Webserver
  - 1 Scheduler
  - PostgreSQL comme base de données

## Prérequis

- Docker
- Docker Compose
- Au moins 4GB de RAM disponible
- Au moins 10GB d'espace disque libre

## Installation

1. Cloner le repository :
```bash
git clone <repository-url>
cd hadoop_tp
```

2. Rendre le script d'installation exécutable :
```bash
chmod +x setup.sh
```

3. Exécuter le script d'installation :
```bash
./setup.sh
```

Le script va :
- Vérifier les prérequis
- Créer les répertoires nécessaires
- Configurer les permissions
- Démarrer les services dans le bon ordre
- Initialiser Airflow
- Tester les connexions

## Interfaces Web

- **HDFS NameNode** : http://localhost:9870
- **YARN ResourceManager** : http://localhost:8088
- **Spark Master** : http://localhost:8080
- **Airflow** : http://localhost:8081 (utilisateur: admin, mot de passe: admin)

## Utilisation

### HDFS

Lister les fichiers dans HDFS :
```bash
docker exec -it namenode hdfs dfs -ls /
```

### Spark

Accéder à Spark SQL :
```bash
docker exec -it spark-master spark-sql
```

Utiliser PySpark :
```bash
docker exec -it spark-master pyspark
```

### Airflow

Les DAGs doivent être placés dans le dossier `./airflow/dags/`. Un exemple de DAG sera fourni pour démarrer.

## Structure des dossiers

```
.
├── airflow/
│   ├── dags/        # DAGs Airflow
│   ├── logs/        # Logs Airflow
│   └── plugins/     # Plugins Airflow
├── data/
│   ├── namenode/    # Données HDFS NameNode
│   ├── datanode1/   # Données HDFS DataNode 1
│   ├── datanode2/   # Données HDFS DataNode 2
│   ├── datanode3/   # Données HDFS DataNode 3
│   ├── postgres/    # Données PostgreSQL
│   └── spark/       # Données Spark
├── docker-compose.yml
├── setup.sh
└── README.md
```

## Tests de connexion

Le script `setup.sh` effectue automatiquement les tests de connexion suivants :

1. Test de la connexion à Spark :
```bash
docker exec -it spark-master spark-sql -e "SHOW DATABASES;"
```

2. Test de la connexion à HDFS :
```bash
docker exec -it namenode hdfs dfs -ls /
```

3. Test de la connexion à YARN :
```bash
docker exec -it resourcemanager yarn node -list
```

## Dépannage

Si vous rencontrez des problèmes :

1. Vérifiez les logs des conteneurs :
```bash
docker-compose logs
```

2. Redémarrez les services :
```bash
docker-compose down
docker-compose up -d
```

3. Réinitialisez l'environnement :
```bash
./setup.sh
```

## Notes importantes

- Le script `setup.sh` supprime toutes les données existantes avant de réinitialiser l'environnement
- Les données sont persistantes dans les dossiers `data/` et `airflow/`
- Les mots de passe par défaut sont configurés pour le développement uniquement
- Pour un environnement de production, modifiez les mots de passe et les clés de sécurité

## Installation Manuelle (en cas de problème avec le script automatique)

Si vous rencontrez des problèmes avec le script d'installation automatique, vous pouvez suivre ces étapes manuellement :

1. Arrêter tous les conteneurs et supprimer les volumes :
```bash
docker-compose down -v
```

2. Nettoyer les données existantes :
```bash
sudo rm -rf ./data/postgres/*
rm -rf ./airflow/logs/*
```

3. Créer les dossiers nécessaires avec les bonnes permissions :
```bash
mkdir -p airflow/dags airflow/logs airflow/plugins
chmod -R 777 airflow/
```

4. Définir l'UID Airflow (remplacez 1000 par votre UID utilisateur si différent) :
```bash
export AIRFLOW_UID=1000
```

5. Démarrer d'abord PostgreSQL :
```bash
docker-compose up -d postgres
```

6. Attendre que PostgreSQL soit prêt (environ 30 secondes), puis initialiser la base de données Airflow :
```bash
docker exec -it airflow-webserver airflow db migrate
```

7. Créer l'utilisateur admin Airflow :
```bash
docker exec -it airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

8. Démarrer les autres services :
```bash
docker-compose up -d
```

9. Vérifier que les services sont bien démarrés :
```bash
docker-compose ps
```

10. Tester les connexions :
```bash
# Test de la connexion à HDFS
docker exec -it namenode hdfs dfs -ls /

# Test de la connexion à YARN
docker exec -it resourcemanager yarn node -list

# Test de la connexion à Spark
docker exec -it spark-master spark-sql -e "SHOW DATABASES;"
```

### Dépannage courant

1. Si PostgreSQL ne démarre pas :
   - Vérifier que le dossier `data/postgres` est vide
   - Vérifier les permissions du dossier
   - Consulter les logs : `docker-compose logs postgres`

2. Si Airflow ne peut pas se connecter à PostgreSQL :
   - Vérifier que PostgreSQL est en cours d'exécution : `docker-compose ps postgres`
   - Vérifier les logs PostgreSQL : `docker-compose logs postgres`
   - Vérifier les logs Airflow : `docker-compose logs airflow-webserver`

3. Si les services ne peuvent pas communiquer entre eux :
   - Vérifier que tous les services sont sur le même réseau : `docker network ls`
   - Vérifier les logs de chaque service
   - Redémarrer les services dans l'ordre : PostgreSQL, puis les autres

## Licence

Ce projet est sous licence MIT.

## DAG MovieLens

Le projet inclut un DAG Airflow pour l'ingestion et la vérification des données MovieLens. Ce DAG effectue les opérations suivantes :

1. Téléchargement des données MovieLens (version 1M)
2. Upload des données vers HDFS
3. Vérification des données avec Spark SQL

### Résultats attendus

Après l'exécution du DAG, vous devriez voir les statistiques suivantes dans les logs de la tâche `verify_data` :

1. **Movies** :
   - 3,883 films au total
   - Format : movieId, title, genres
   - Exemple : "Toy Story (1995)" avec les genres "Animation|Children's|Comedy"

2. **Ratings** :
   - 1,000,209 évaluations au total
   - Format : userId, movieId, rating (1-5), timestamp
   - Exemple : L'utilisateur 1 a donné une note de 5 au film 1193

3. **Users** :
   - 6,040 utilisateurs au total
   - Format : userId, gender (M/F), age, occupation, zipcode
   - Exemple : L'utilisateur 1 est une femme (F) de 1 an (catégorie d'âge), avec l'occupation 10, du code postal 48067

### Exécution du DAG

Le DAG est automatiquement copié et déclenché lors de l'exécution du script `setup.sh`. Vous pouvez également le déclencher manuellement via l'interface Airflow ou avec la commande :

```bash
docker exec -it airflow-webserver airflow dags trigger movielens_ingestion
```

### Vérification des résultats

Pour vérifier les résultats :
1. Accédez à l'interface Airflow (http://localhost:8081)
2. Connectez-vous avec les identifiants par défaut (admin/admin)
3. Sélectionnez le DAG `movielens_ingestion`
4. Cliquez sur la dernière exécution
5. Vérifiez les logs de la tâche `verify_data` 