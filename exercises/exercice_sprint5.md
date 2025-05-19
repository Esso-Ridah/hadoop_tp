# Sprint 2 : Pipeline Complet de Recommandation (Obligatoire)

## Objectifs
L'objectif de ce sprint est de créer un pipeline complet (un DAG final) qui intègre toutes les étapes du traitement des données, de l'ingestion jusqu'à la génération des recommandations finales. Ce pipeline doit être robuste, reproductible et facilement maintenable.

## Exercices

### 1. Ingestion des Données
- Créer un script d'ingestion qui :
  - Télécharge les données MovieLens depuis l'API
  - Vérifie l'intégrité des fichiers
  - Charge les données dans HDFS
  - Valide le format et la qualité des données

### 2. Prétraitement des Données
- Implémenter un pipeline de nettoyage qui :
  - Gère les valeurs manquantes
  - Normalise les données
  - Filtre les anomalies
  - Crée les features nécessaires
  - Sauvegarde les données nettoyées

### 3. Entraînement du Modèle
- Développer un pipeline d'entraînement qui :
  - Divise les données en train/validation/test
  - Optimise les hyperparamètres
  - Entraîne le modèle ALS
  - Évalue les performances
  - Sauvegarde le modèle

### 4. Génération des Recommandations
- Créer un pipeline de recommandation qui :
  - Charge le modèle entraîné
  - Génère les recommandations
  - Applique les filtres nécessaires
  - Sauvegarde les résultats

### 5. Orchestration avec Airflow
- Créer un DAG Airflow qui :
  - Orchestre toutes les étapes
  - Gère les dépendances
  - Gère les erreurs
  - Envoie des notifications

## Livrables Attendus

1. **Code Source**
   - Scripts Python pour chaque étape
   - DAG Airflow
   - Tests unitaires
   - Documentation du code

2. **Documentation**
   - Architecture du pipeline
   - Diagramme de flux
   - Guide d'utilisation
   - Procédures de maintenance

3. **Présentation**
   - Démonstration du pipeline
   - Résultats obtenus
   - Points d'amélioration
   - Recommandations

## Critères d'Évaluation

1. **Qualité du Code** (25%)
   - Structure modulaire
   - Documentation
   - Gestion des erreurs
   - Tests unitaires

2. **Robustesse** (25%)
   - Gestion des erreurs
   - Validation des données
   - Monitoring
   - Reprise sur erreur

3. **Performance** (25%)
   - Temps de traitement
   - Utilisation des ressources
   - Optimisation
   - Scalabilité

4. **Maintenabilité** (25%)
   - Documentation
   - Modularité
   - Configuration
   - Tests

## Exemple de Structure

```python
# pipeline.py
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
import logging

class RecommendationPipeline:
    def __init__(self, config):
        self.config = config
        self.spark = SparkSession.builder \
            .appName("MovieRecommendationPipeline") \
            .getOrCreate()
        
    def ingest_data(self):
        """Étape 1: Ingestion des données"""
        logging.info("Début de l'ingestion des données")
        # Code d'ingestion
        return self
        
    def preprocess_data(self):
        """Étape 2: Prétraitement des données"""
        logging.info("Début du prétraitement")
        # Code de prétraitement
        return self
        
    def train_model(self):
        """Étape 3: Entraînement du modèle"""
        logging.info("Début de l'entraînement")
        # Code d'entraînement
        return self
        
    def generate_recommendations(self):
        """Étape 4: Génération des recommandations"""
        logging.info("Génération des recommandations")
        # Code de génération
        return self
        
    def run(self):
        """Exécution du pipeline complet"""
        try:
            return (self.ingest_data()
                    .preprocess_data()
                    .train_model()
                    .generate_recommendations())
        except Exception as e:
            logging.error(f"Erreur dans le pipeline: {str(e)}")
            raise
```

## DAG Airflow

```python
# recommendation_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'movie_recommendation_pipeline',
    default_args=default_args,
    description='Pipeline complet de recommandation de films',
    schedule_interval=timedelta(days=1),
)

# Définition des tâches
ingest_task = PythonOperator(
    # complété le Code
    ,
)

preprocess_task = PythonOperator(
    # complété le Code
    ,
)

train_task = PythonOperator(
    # complété le Code
    ,
)

recommend_task = PythonOperator(
    # complété le Code
    ,
)

# Définition des dépendances
... >> ... >> ...
```

## Conseils d'Implémentation

1. **Modularité**
   - Séparer les responsabilités
   - Utiliser des classes
   - Créer des modules réutilisables

2. **Gestion des Erreurs**
   - Implémenter des retries
   - Logger les erreurs
   - Notifier en cas de problème

3. **Monitoring**
   - Ajouter des métriques
   - Créer des dashboards
   - Surveiller les performances

4. **Tests**
   - Tests unitaires
   - Tests d'intégration
   - Tests de performance

## Ressources

1. **Documentation**
   - [Airflow Documentation](https://airflow.apache.org/docs/)
   - [Spark Documentation](https://spark.apache.org/docs/)
   - [HDFS Documentation](https://hadoop.apache.org/docs/)

2. **Exemples**
   - Voir `/examples/solutions/sprint2/pipeline.py`
   - Étudier les patterns d'implémentation
   - Analyser les bonnes pratiques

## Questions Fréquentes

1. **Comment gérer les erreurs ?**
   - Utiliser des try/catch
   - Implémenter des retries
   - Logger les erreurs
   - Notifier les administrateurs

2. **Comment optimiser les performances ?**
   - Utiliser le caching
   - Optimiser les partitions
   - Paralléliser les tâches
   - Surveiller les ressources

3. **Comment maintenir le pipeline ?**
   - Documenter le code
   - Ajouter des tests
   - Créer des dashboards
   - Automatiser les déploiements

## Pour pouvez aller plus loin

Après avoir complété ce sprint, vous pourrez :
1. Ajouter des fonctionnalités de monitoring
2. Implémenter des tests automatisés
3. Créer une interface utilisateur
4. Optimiser les performances 