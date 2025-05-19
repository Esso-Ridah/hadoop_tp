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

## Tests de connexion et vérifications

### 1. Tests de connexion HDFS

Vérifier que HDFS est accessible et fonctionne correctement :

```bash
# Lister le contenu de la racine HDFS
docker exec -it namenode hdfs dfs -ls /

# Vérifier l'état des datanodes
docker exec -it namenode hdfs dfsadmin -report | grep "Live datanodes"

# Vérifier l'espace disponible
docker exec -it namenode hdfs dfsadmin -report | grep "DFS Used"

# Vérifier les permissions du répertoire Airflow
docker exec -it namenode hdfs dfs -ls /user/airflow
```

### 2. Tests d'écriture/lecture HDFS

Vérifier que les opérations d'écriture et de lecture fonctionnent :

```bash
# Test d'écriture simple
docker exec -it namenode bash -c 'echo "Test HDFS write/read" > test.txt && hdfs dfs -put test.txt /user/airflow/test.txt'

# Vérifier que le fichier a été écrit
docker exec -it namenode hdfs dfs -ls /user/airflow/test.txt

# Lire le contenu du fichier
docker exec -it namenode hdfs dfs -cat /user/airflow/test.txt

# Test avec un fichier plus grand
docker exec -it namenode bash -c 'dd if=/dev/zero of=large_file.txt bs=1M count=10 && hdfs dfs -put large_file.txt /user/airflow/large_file.txt'

# Vérifier la réplication du fichier
docker exec -it namenode hdfs dfs -ls /user/airflow/large_file.txt
```

### 3. Tests de connexion YARN

Vérifier que YARN est opérationnel :

```bash
# Lister les nœuds YARN
docker exec -it resourcemanager yarn node -list

# Vérifier les applications en cours
docker exec -it resourcemanager yarn application -list

# Vérifier la capacité du cluster
docker exec -it resourcemanager yarn node -list | grep "Memory"
```

### 4. Tests de connexion Spark

Vérifier que Spark est correctement configuré :

```bash
# Vérifier les bases de données disponibles
docker exec -it spark-master spark-sql -e "SHOW DATABASES;"

# Tester une requête simple
docker exec -it spark-master spark-sql -e "SELECT 1 as test;"

# Vérifier la connexion à HDFS depuis Spark
docker exec -it spark-master spark-sql -e "CREATE TABLE test (id INT) LOCATION '/user/airflow/test_table';"
```

### 5. Tests de connexion Airflow

Vérifier que Airflow est correctement configuré :

```bash
# Vérifier l'état des services Airflow
docker exec -it airflow-webserver airflow db check

# Lister les DAGs disponibles
docker exec -it airflow-webserver airflow dags list

# Vérifier les connexions configurées
docker exec -it airflow-webserver airflow connections list
```

### 6. Tests de performance

Vérifier les performances du cluster :

```bash
# Test de performance HDFS
docker exec -it namenode bash -c 'time hdfs dfs -put /etc/hosts /user/airflow/test_perf.txt'

# Test de performance Spark
docker exec -it spark-master spark-sql -e "SELECT count(*) FROM range(1000000);"
```

### 7. Vérification des logs

En cas de problème, vérifier les logs des différents services :

```bash
# Logs HDFS
docker exec -it namenode cat $HADOOP_HOME/logs/hadoop-hadoop-namenode-namenode.log

# Logs YARN
docker exec -it resourcemanager cat $HADOOP_HOME/logs/yarn-hadoop-resourcemanager-resourcemanager.log

# Logs Spark
docker exec -it spark-master cat $SPARK_HOME/logs/spark.log

# Logs Airflow
docker exec -it airflow-webserver cat $AIRFLOW_HOME/logs/dag_id/task_id/execution_date/attempt_number.log
```

### 8. Vérification de la santé du cluster

Vérifier l'état général du cluster :

```bash
# État des conteneurs
docker-compose ps

# Utilisation des ressources
docker stats

# Vérifier les erreurs dans les logs
docker-compose logs | grep -i "error"
```

Ces tests peuvent être exécutés manuellement ou automatiquement via le script `setup.sh`. En cas d'échec d'un test, consultez la section Dépannage pour plus d'informations.

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

## DAGs MovieLens

Le projet inclut deux DAGs Airflow pour le traitement des données MovieLens :

### 1. DAG d'Ingestion (movielens_ingestion)
Ce DAG effectue les opérations suivantes :
1. Téléchargement des données MovieLens (version 1M)
2. Upload des données vers HDFS
3. Vérification des données avec Spark SQL

### 2. DAG de Recommandation (movie_recommendation)
Ce DAG implémente un système de recommandation de films en utilisant Spark ML :
1. Préparation des données (nettoyage et transformation)
2. Entraînement du modèle ALS (Alternating Least Squares)
3. Génération des recommandations pour tous les utilisateurs

### Résultats attendus

#### DAG d'Ingestion
- Données MovieLens disponibles dans HDFS sous `/user/airflow/movielens/`
- Tables Spark SQL créées et vérifiées

#### DAG de Recommandation
- Modèle ALS entraîné et sauvegardé dans HDFS
- Recommandations générées pour chaque utilisateur
- Métriques de performance (RMSE) calculées

### Vérification de l'installation

Le script `setup.sh` effectue automatiquement les vérifications suivantes :

1. Test de la connexion à HDFS :
```bash
docker exec -it namenode hdfs dfs -ls /
```

2. Vérification des datanodes :
```bash
docker exec -it namenode hdfs dfsadmin -report | grep "Live datanodes"
```

3. Test d'écriture/lecture dans HDFS :
```bash
docker exec -it namenode bash -c 'echo "Test HDFS write/read" > test.txt && hdfs dfs -put test.txt /user/airflow/test.txt'
```

4. Test de la connexion à YARN :
```bash
docker exec -it resourcemanager yarn node -list
```

5. Test de la connexion à Spark :
```bash
docker exec -it spark-master spark-sql -e "SHOW DATABASES;"
```

### Dépannage

Si vous rencontrez des problèmes :

1. Vérifiez les logs des conteneurs :
```bash
docker-compose logs
```

2. Vérifiez l'état des datanodes :
```bash
docker exec -it namenode hdfs dfsadmin -report
```

3. Vérifiez les permissions HDFS :
```bash
docker exec -it namenode hdfs dfs -ls /user/airflow
```

4. Redémarrez les services :
```bash
docker-compose down
docker-compose up -d
```

5. Réinitialisez l'environnement :
```bash
./setup.sh
```

## Notes importantes

- Le script `setup.sh` supprime toutes les données existantes avant de réinitialiser l'environnement
- Les données sont persistantes dans les dossiers `data/` et `airflow/`
- Les mots de passe par défaut sont configurés pour le développement uniquement
- Pour un environnement de production, modifiez les mots de passe et les clés de sécurité
- Le DAG de recommandation utilise 10% des données pour les tests, modifiez le paramètre `sample(fraction=0.1)` pour utiliser l'ensemble des données 

## Visualisation des recommandations (Flask)

Une interface web Flask permet de visualiser les recommandations générées pour les utilisateurs MovieLens.

### Lancer l'interface Flask

L'interface Flask est automatiquement déployée par le script `setup.sh`. Elle est accessible à l'adresse :

    http://localhost:5000

Pour voir les logs :
```bash
docker logs movie-recommendation-viewer
```
Pour arrêter l'application :
```bash
docker stop movie-recommendation-viewer
```

### Tester la connectivité réseau depuis le conteneur Flask

Pour diagnostiquer la connectivité réseau entre le conteneur Flask et le cluster Hadoop :
```bash
docker exec -it movie-recommendation-viewer ping -c 4 namenode
```

Vous pouvez aussi utiliser d'autres outils réseau comme `curl`, `netstat`, ou `ip addr` dans le conteneur :
```bash
docker exec -it movie-recommendation-viewer ip addr
```

### Utilisation de l'interface

- Accédez à http://localhost:5000
- Entrez un identifiant utilisateur pour voir ses recommandations.

## Système de Recommandation de Films avec Hadoop et Spark

Ce projet implémente un système de recommandation de films en utilisant Hadoop et Spark, avec une interface web pour visualiser les recommandations.

## Architecture

Le système est composé de plusieurs composants :

1. **Hadoop** : Stockage distribué des données
   - NameNode : Gestion des métadonnées HDFS
   - DataNodes : Stockage des données
   - ResourceManager : Gestion des ressources YARN
   - NodeManagers : Exécution des tâches

2. **Spark** : Traitement des données
   - Spark Master : Coordination des tâches
   - Spark Workers : Exécution des tâches Spark

3. **Airflow** : Orchestration des workflows
   - Webserver : Interface web
   - Scheduler : Planification des tâches

4. **PostgreSQL** : Base de données pour Airflow

5. **API REST** : Interface pour accéder aux recommandations
   - Endpoint `/recommendations/<user_id>` : Obtenir les recommandations pour un utilisateur
   - Endpoint `/metrics` : Obtenir les métriques du système
   - Endpoint `/health` : Vérifier l'état du service

6. **Monitoring** : Surveillance du système
   - Prometheus : Collecte des métriques
   - Grafana : Visualisation des métriques

## Prérequis

- Docker
- Docker Compose
- Python 3.9+
- Git

## Installation

1. Cloner le repository :
```bash
git clone <repository-url>
cd <repository-name>
```

2. Exécuter le script de configuration :
```bash
./setup.sh
```

3. Démarrer les services :
```bash
docker-compose up -d
```

## Accès aux Services

- **Interface Web** : http://localhost:8081
- **API REST** : http://localhost:5000
- **Prometheus** : http://localhost:9090
- **Grafana** : http://localhost:3000 (admin/admin)

## Utilisation

### Interface Web

1. Accédez à l'interface web à l'adresse http://localhost:8081
2. Connectez-vous avec les identifiants par défaut (airflow/airflow)
3. Activez le DAG "movie_recommendation"
4. Déclenchez une exécution manuelle

### API REST

1. Obtenir les recommandations pour un utilisateur :
```bash
curl http://localhost:5000/recommendations/1
```

2. Vérifier les métriques du système :
```bash
curl http://localhost:5000/metrics
```

3. Vérifier l'état du service :
```bash
curl http://localhost:5000/health
```

### Monitoring

1. Accédez à Grafana à l'adresse http://localhost:3000
2. Connectez-vous avec les identifiants par défaut (admin/admin)
3. Le dashboard "Recommandations" est automatiquement configuré avec :
   - Taux de recommandations
   - Temps de réponse moyen
   - Taux d'erreur

## Structure des Données

Les données sont stockées dans HDFS sous le chemin `/user/airflow/movielens/` avec les sous-répertoires suivants :
- `raw` : Données brutes
- `processed` : Données traitées
- `recommendations` : Recommandations générées
- `stats` : Statistiques du système

## Monitoring

Le système est surveillé via Prometheus et Grafana :

1. **Prometheus** collecte les métriques suivantes :
   - Nombre total de recommandations
   - Temps de réponse des requêtes
   - Nombre d'erreurs
   - Métriques Hadoop et Spark

2. **Grafana** visualise ces métriques avec :
   - Un dashboard "Recommandations" préconfiguré
   - Des graphiques en temps réel
   - Des alertes configurables

## Développement

### Structure du Projet

```
.
├── airflow/
│   ├── dags/
│   │   ├── api/
│   │   │   ├── Dockerfile
│   │   │   ├── requirements.txt
│   │   │   └── recommendation_api.py
│   │   ├── monitoring/
│   │   │   ├── prometheus.yml
│   │   │   └── grafana_dashboard.json
│   │   └── movie_recommendation_dag.py
│   ├── Dockerfile
│   └── requirements.txt
├── hadoop/
│   └── Dockerfile
├── docker-compose.yml
├── setup.sh
└── README.md
```

### Ajout de Nouvelles Fonctionnalités

1. **API** :
   - Modifier `airflow/dags/api/recommendation_api.py`
   - Ajouter les dépendances dans `requirements.txt`
   - Reconstruire l'image : `docker-compose build recommendation-api`

2. **Monitoring** :
   - Modifier `airflow/dags/monitoring/prometheus.yml` pour ajouter des métriques
   - Modifier `airflow/dags/monitoring/grafana_dashboard.json` pour ajouter des visualisations
   - Recharger la configuration : `docker-compose restart prometheus grafana`

## Dépannage

1. **Problèmes de Connexion** :
   - Vérifier que tous les services sont en cours d'exécution : `docker-compose ps`
   - Vérifier les logs : `docker-compose logs <service-name>`

2. **Problèmes de Performance** :
   - Vérifier les métriques dans Grafana
   - Ajuster les paramètres de mémoire dans `docker-compose.yml`

3. **Problèmes de Données** :
   - Vérifier les permissions HDFS : `hdfs dfs -ls /user/airflow/movielens`
   - Vérifier les logs Airflow pour les erreurs de traitement

## Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

# Projet de Recommandation de Films avec Hadoop

## Vue d'ensemble

Ce projet implémente un système de recommandation de films utilisant :
- Hadoop HDFS pour le stockage
- YARN pour la gestion des ressources
- Apache Spark pour le traitement
- Apache Airflow pour l'orchestration
- Flask pour l'interface de visualisation

## Prérequis

- Docker
- Docker Compose
- Au moins 8GB de RAM
- Au moins 20GB d'espace disque libre

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

## Installation de l'Interface de Visualisation

1. Installer les dépendances Python :
```bash
pip install flask pandas numpy matplotlib seaborn
```

2. Construire l'image Docker pour l'interface :
```bash
docker build -t movie-recommendation-viewer -f Dockerfile.viewer .
```

3. Lancer le conteneur de l'interface :
```bash
docker run -d --name movie-viewer --network hadoop_tp_hadoop_network -p 5000:5000 movie-recommendation-viewer
```

## Interfaces Web

### HDFS
- URL : http://localhost:9870
- Credentials : admin/admin

### YARN
- URL : http://localhost:8088
- Credentials : admin/admin

### Spark
- URL : http://localhost:8080
- Credentials : admin/admin

### Airflow
- URL : http://localhost:8080
- Credentials : airflow/airflow

### Interface de Visualisation
- URL : http://localhost:5000
- Fonctionnalités :
  - Sélection d'un utilisateur via un menu déroulant
  - Affichage des recommandations de films
  - Visualisation des scores de recommandation
  - Filtrage par genre

## Utilisation

### HDFS
```bash
# Lister les fichiers
hdfs dfs -ls /user/airflow/movielens

# Copier un fichier local vers HDFS
hdfs dfs -put local_file.txt /user/airflow/movielens/
```

### Spark
```bash
# Lancer un job Spark
spark-submit --master yarn your_script.py
```

### Airflow
1. Accéder à l'interface web
2. Activer le DAG `movie_recommendation`
3. Déclencher manuellement ou attendre le planning

### Interface de Visualisation
1. Ouvrir http://localhost:5000 dans votre navigateur
2. Sélectionner un utilisateur dans le menu déroulant
3. Consulter les recommandations de films générées
4. Utiliser les filtres pour affiner les résultats

## Structure des Dossiers

```
.
├── airflow/
│   └── dags/          # DAGs Airflow
├── examples/
│   └── solutions/     # Solutions des sprints
├── tests/            # Tests unitaires
└── docs/             # Documentation
```

## Tests de Connexion

### HDFS
```bash
hdfs dfs -ls /
```

### Spark
```bash
spark-submit --master yarn --deploy-mode client test_spark.py
```

### Airflow
```bash
airflow test movie_recommendation start_date 2024-01-01
```

## Dépannage

### Interface de Visualisation
Si l'interface n'est pas accessible :
1. Vérifier que le conteneur est en cours d'exécution :
```bash
docker ps | grep movie-viewer
```

2. Vérifier les logs du conteneur :
```bash
docker logs movie-viewer
```

3. Redémarrer le conteneur si nécessaire :
```bash
docker restart movie-viewer
```

4. Vérifier la connectivité réseau :
```bash
docker network inspect hadoop_tp_hadoop_network
```

## Support

Pour toute question ou problème :
1. Consulter la documentation
2. Vérifier les issues existantes
3. Créer une nouvelle issue si nécessaire 