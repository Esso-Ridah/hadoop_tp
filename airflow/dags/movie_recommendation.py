from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
import os
import logging

# Configuration du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'movie_recommendation',
    default_args=default_args,
    description='DAG pour le système de recommandation de films',
    schedule_interval=None,
    start_date=datetime(2025, 5, 17),
    catchup=False,
)

def prepare_data(**context):
    """
    Prépare les données pour l'entraînement du modèle ALS
    - Charge les données depuis HDFS
    - Nettoie et transforme les données
    - Sauvegarde les données préparées
    """
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, when
    
    # Créer la session Spark
    spark = SparkSession.builder \
        .appName("Movie Recommendation - Data Preparation") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    try:
        # Charger les données depuis les fichiers .dat
        ratings_df = spark.read \
            .option("delimiter", "::") \
            .option("header", "false") \
            .csv("hdfs://namenode:9000/user/airflow/movielens/ratings.dat") \
            .toDF("userId", "movieId", "rating", "timestamp")
        
        movies_df = spark.read \
            .option("delimiter", "::") \
            .option("header", "false") \
            .csv("hdfs://namenode:9000/user/airflow/movielens/movies.dat") \
            .toDF("movieId", "title", "genres")
        
        # Nettoyer les données
        # - Supprimer les doublons
        # - Filtrer les notes invalides
        # - Convertir les types
        clean_ratings = ratings_df \
            .dropDuplicates(['userId', 'movieId']) \
            .filter(col('rating').between(1, 5)) \
            .select(
                col('userId').cast('integer'),
                col('movieId').cast('integer'),
                col('rating').cast('float')
            )
        
        # Échantillonner 10% des données pour les tests
        clean_ratings = clean_ratings.sample(fraction=0.1, seed=42)
        
        # Sauvegarder les données préparées en parquet
        clean_ratings.write \
            .mode('overwrite') \
            .parquet("hdfs://namenode:9000/user/airflow/movielens/ratings_clean.parquet")
        
        # Afficher quelques statistiques
        logging.info(f"Nombre total de notes : {clean_ratings.count()}")
        logging.info(f"Nombre d'utilisateurs uniques : {clean_ratings.select('userId').distinct().count()}")
        logging.info(f"Nombre de films uniques : {clean_ratings.select('movieId').distinct().count()}")
        
    finally:
        spark.stop()

def train_als_model(**context):
    """
    Entraîne le modèle ALS avec les paramètres optimaux
    - Charge les données préparées
    - Configure et entraîne le modèle
    - Évalue les performances
    - Sauvegarde le modèle
    """
    from pyspark.sql import SparkSession
    from pyspark.ml.recommendation import ALS
    from pyspark.ml.evaluation import RegressionEvaluator
    from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
    
    # Créer la session Spark avec des configurations optimisées
    spark = SparkSession.builder \
        .appName("Movie Recommendation - ALS Training") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.maxResultSize", "1g") \
        .config("spark.sql.shuffle.partitions", "10") \
        .config("spark.default.parallelism", "10") \
        .getOrCreate()
    
    try:
        # Charger les données préparées
        ratings_df = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/ratings_clean.parquet")
        
        # Diviser en ensembles d'entraînement et de test
        train, test = ratings_df.randomSplit([0.8, 0.2], seed=42)
        
        # Créer le modèle ALS
        als = ALS(
            userCol="userId",
            itemCol="movieId",
            ratingCol="rating",
            coldStartStrategy="drop",
            nonnegative=True
        )
        
        # Définir une grille de paramètres réduite pour les tests
        param_grid = ParamGridBuilder() \
            .addGrid(als.rank, [10, 50]) \
            .addGrid(als.regParam, [0.01, 0.1]) \
            .addGrid(als.maxIter, [10]) \
            .build()
        
        # Configurer l'évaluateur
        evaluator = RegressionEvaluator(
            metricName="rmse",
            labelCol="rating",
            predictionCol="prediction"
        )
        
        # Configurer la validation croisée avec 2 folds
        cv = CrossValidator(
            estimator=als,
            estimatorParamMaps=param_grid,
            evaluator=evaluator,
            numFolds=2,
            parallelism=2  # Limiter le parallélisme pour éviter les problèmes de mémoire
        )
        
        # Entraîner le modèle
        cv_model = cv.fit(train)
        
        # Évaluer sur l'ensemble de test
        predictions = cv_model.transform(test)
        rmse = evaluator.evaluate(predictions)
        
        # Afficher les résultats
        logging.info(f"RMSE sur l'ensemble de test : {rmse}")
        
        # Sauvegarder le meilleur modèle
        best_model = cv_model.bestModel
        best_model.save("hdfs://namenode:9000/user/airflow/movielens/als_model")
        
        # Afficher les meilleurs paramètres
        logging.info(f"Meilleurs paramètres : {best_model.extractParamMap()}")
        
    finally:
        spark.stop()

def generate_recommendations(**context):
    """
    Génère les recommandations pour tous les utilisateurs
    - Charge le modèle entraîné
    - Génère les recommandations
    - Sauvegarde les résultats
    """
    from pyspark.sql import SparkSession
    from pyspark.ml.recommendation import ALSModel
    
    # Créer la session Spark
    spark = SparkSession.builder \
        .appName("Movie Recommendation - Generate Recommendations") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    try:
        # Charger le modèle
        model = ALSModel.load("hdfs://namenode:9000/user/airflow/movielens/als_model")
        
        # Générer les recommandations pour tous les utilisateurs
        # (limité à 10 recommandations par utilisateur)
        recommendations = model.recommendForAllUsers(10)
        
        # Sauvegarder les recommandations en parquet
        recommendations.write \
            .mode('overwrite') \
            .parquet("hdfs://namenode:9000/user/airflow/movielens/recommendations.parquet")
        
        # Afficher quelques statistiques
        logging.info(f"Nombre d'utilisateurs avec recommandations : {recommendations.count()}")
        
    finally:
        spark.stop()

# Tâches du DAG
prepare_data_task = PythonOperator(
    task_id='prepare_data',
    python_callable=prepare_data,
    dag=dag,
)

train_model_task = PythonOperator(
    task_id='train_als_model',
    python_callable=train_als_model,
    dag=dag,
)

generate_recommendations_task = PythonOperator(
    task_id='generate_recommendations',
    python_callable=generate_recommendations,
    dag=dag,
)

# Définition des dépendances
prepare_data_task >> train_model_task >> generate_recommendations_task 