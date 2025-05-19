from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pyspark.sql import SparkSession
from als_optimization import (
    calculate_precision_at_k,
    calculate_diversity,
    handle_cold_start,
    optimize_als_parameters
)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def load_sample_data(spark, sample_fraction=0.1):
    """Charge un échantillon des données pour les tests"""
    print(f"Chargement de {sample_fraction*100}% des données...")
    
    # Charger les données depuis HDFS
    ratings = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/ratings_clean.parquet")
    movies = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/movies.parquet")
    
    # Échantillonner les données
    ratings_sample = ratings.sample(fraction=sample_fraction, seed=42)
    movies_sample = movies.sample(fraction=sample_fraction, seed=42)
    
    print(f"Taille de l'échantillon ratings: {ratings_sample.count()} lignes")
    print(f"Taille de l'échantillon movies: {movies_sample.count()} lignes")
    
    return ratings_sample, movies_sample

def test_metrics(**context):
    import os
    
    # Configuration des variables d'environnement Spark
    os.environ.update({
        'JAVA_HOME': '/usr/lib/jvm/java-8-openjdk-amd64',
        'SPARK_HOME': '/opt/bitnami/spark',
        'HADOOP_CONF_DIR': '/opt/bitnami/spark/conf',
        'PYTHONPATH': '/opt/bitnami/spark/python:/opt/bitnami/spark/python/lib/py4j-0.10.9.7-src.zip',
    })
    
    spark = SparkSession.builder \
        .appName("ALS Optimization Test") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
        .config("spark.hadoop.dfs.datanode.use.datanode.hostname", "true") \
        .config("spark.driver.extraJavaOptions", "-Djava.net.preferIPv4Stack=true") \
        .config("spark.executor.extraJavaOptions", "-Djava.net.preferIPv4Stack=true") \
        .getOrCreate()
    
    # Charger un échantillon des données
    ratings, movies = load_sample_data(spark)
    
    # Tester precision@k
    precision = calculate_precision_at_k(ratings, k=10)
    print(f"Precision@10: {precision}")
    
    # Tester diversity
    diversity = calculate_diversity(movies, k=10)
    print(f"Diversity: {diversity}")
    
    spark.stop()

def test_optimization(**context):
    import os
    
    # Configuration des variables d'environnement Spark
    os.environ.update({
        'JAVA_HOME': '/usr/lib/jvm/java-8-openjdk-amd64',
        'SPARK_HOME': '/opt/bitnami/spark',
        'HADOOP_CONF_DIR': '/opt/bitnami/spark/conf',
        'PYTHONPATH': '/opt/bitnami/spark/python:/opt/bitnami/spark/python/lib/py4j-0.10.9.7-src.zip',
    })
    
    spark = SparkSession.builder \
        .appName("ALS Optimization Test") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
        .config("spark.hadoop.dfs.datanode.use.datanode.hostname", "true") \
        .config("spark.driver.extraJavaOptions", "-Djava.net.preferIPv4Stack=true") \
        .config("spark.executor.extraJavaOptions", "-Djava.net.preferIPv4Stack=true") \
        .getOrCreate()
    
    # Charger un échantillon des données
    ratings, _ = load_sample_data(spark)
    
    # Tester l'optimisation des paramètres
    best_params = optimize_als_parameters(ratings)
    print(f"Meilleurs paramètres: {best_params}")
    
    spark.stop()

def test_cold_start(**context):
    import os
    
    # Configuration des variables d'environnement Spark
    os.environ.update({
        'JAVA_HOME': '/usr/lib/jvm/java-8-openjdk-amd64',
        'SPARK_HOME': '/opt/bitnami/spark',
        'HADOOP_CONF_DIR': '/opt/bitnami/spark/conf',
        'PYTHONPATH': '/opt/bitnami/spark/python:/opt/bitnami/spark/python/lib/py4j-0.10.9.7-src.zip',
    })
    
    spark = SparkSession.builder \
        .appName("ALS Optimization Test") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
        .config("spark.hadoop.dfs.datanode.use.datanode.hostname", "true") \
        .config("spark.driver.extraJavaOptions", "-Djava.net.preferIPv4Stack=true") \
        .config("spark.executor.extraJavaOptions", "-Djava.net.preferIPv4Stack=true") \
        .getOrCreate()
    
    # Charger un échantillon des données
    ratings, movies = load_sample_data(spark)
    
    # Tester la gestion du cold start
    cold_start_recommendations = handle_cold_start(ratings, movies)
    print(f"Nombre de recommandations cold start: {cold_start_recommendations.count()}")
    
    spark.stop()

with DAG(
    'als_optimization_test',
    default_args=default_args,
    description='Test des fonctions d\'optimisation ALS',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['test', 'als', 'optimization'],
) as dag:

    test_metrics_task = PythonOperator(
        task_id='test_metrics',
        python_callable=test_metrics,
    )

    test_optimization_task = PythonOperator(
        task_id='test_optimization',
        python_callable=test_optimization,
    )

    test_cold_start_task = PythonOperator(
        task_id='test_cold_start',
        python_callable=test_cold_start,
    )

    test_metrics_task >> test_optimization_task >> test_cold_start_task 