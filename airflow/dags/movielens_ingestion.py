from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
import os, tempfile, subprocess, requests
from urllib.parse import urljoin
from airflow.utils.dates import days_ago
import logging
import json
import time

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
    'movielens_ingestion',
    default_args=default_args,
    description='DAG pour l\'ingestion des données MovieLens',
    schedule_interval=None,
    start_date=datetime(2025, 5, 17),
    catchup=False,
)

# Variables d'environnement pour Spark
spark_env = {
    'JAVA_HOME': '/usr/lib/jvm/java-17-openjdk-amd64',
    'SPARK_HOME': '/opt/spark',
    'HADOOP_CONF_DIR': '/opt/spark/conf',
    'PYTHONPATH': '/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip',
}

def download_movielens_data():
    """Télécharge les données MovieLens et les stocke temporairement"""
    logging.info("Starting download_movielens_data function")
    
    # URL des données MovieLens (version 1M)
    base_url = "https://files.grouplens.org/datasets/movielens/ml-1m.zip"
    logging.info(f"Downloading from URL: {base_url}")
    
    # Créer un dossier temporaire persistant pour ce run
    temp_dir = tempfile.mkdtemp(prefix="ml1m_")
    logging.info(f"Created temporary directory: {temp_dir}")
    
    # Vérifier que le dossier existe et est accessible en écriture
    if not os.path.exists(temp_dir):
        raise Exception(f"Temporary directory {temp_dir} was not created")
    if not os.access(temp_dir, os.W_OK):
        raise Exception(f"Temporary directory {temp_dir} is not writable")
    
    zip_path = os.path.join(temp_dir, "ml-1m.zip")
    logging.info(f"Will save zip file to: {zip_path}")
    
    try:
        # Tester la connexion au site
        logging.info("Testing connection to files.grouplens.org...")
        test_response = requests.head(base_url)
        test_response.raise_for_status()
        logging.info("Connection test successful")
        
        # Télécharger le fichier
        logging.info("Starting file download...")
        subprocess.run(['curl', '-L', '-o', zip_path, base_url], check=True)
        logging.info("File download completed successfully")
        
        # Vérifier que le fichier a été téléchargé
        if not os.path.exists(zip_path):
            raise Exception(f"Downloaded file not found at {zip_path}")
        logging.info(f"Downloaded file size: {os.path.getsize(zip_path)} bytes")
        
        # Extraire le zip dans ce dossier
        logging.info("Starting file extraction...")
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        logging.info("File extraction completed")
        
        # Vérifier que les fichiers ont été extraits
        extracted_dir = os.path.join(temp_dir, "ml-1m")
        if not os.path.exists(extracted_dir):
            raise Exception(f"Extracted directory not found at {extracted_dir}")
        
        required_files = ['movies.dat', 'ratings.dat', 'users.dat']
        for file in required_files:
            file_path = os.path.join(extracted_dir, file)
            if not os.path.exists(file_path):
                raise Exception(f"Required file {file} not found in extracted directory")
            logging.info(f"Found required file: {file}")
        
        logging.info("All files extracted successfully")
        return extracted_dir
        
    except Exception as e:
        logging.error(f"Error in download_movielens_data: {str(e)}")
        raise

def upload_to_hdfs(**context):
    """Upload les fichiers vers HDFS"""
    # Configuration WebHDFS
    webhdfs_url = "http://namenode:9870/webhdfs/v1"
    user = "airflow"
    
    # Créer le dossier dans HDFS
    hdfs_path = "/user/airflow/movielens"
    mkdir_url = f"{webhdfs_url}{hdfs_path}?op=MKDIRS&user.name={user}"
    response = requests.put(mkdir_url)
    response.raise_for_status()
    
    # Chemin local des fichiers extraits
    local_dir = context['task_instance'].xcom_pull(task_ids='download_movielens_data')
    
    # Upload chaque fichier
    for filename in ['movies.dat', 'ratings.dat', 'users.dat']:
        local_path = os.path.join(local_dir, filename)
        hdfs_file_path = f"{hdfs_path}/{filename}"
        
        # Créer le fichier dans HDFS
        create_url = f"{webhdfs_url}{hdfs_file_path}?op=CREATE&user.name={user}&overwrite=true"
        response = requests.put(create_url, allow_redirects=False)
        response.raise_for_status()
        
        # Upload le contenu du fichier
        upload_url = response.headers['Location']
        with open(local_path, 'rb') as f:
            response = requests.put(upload_url, data=f)
            response.raise_for_status()

def verify_data_task(**context):
    """Exécute les requêtes de vérification et retourne les résultats"""
    from pyspark.sql import SparkSession
    import os
    os.environ.update({
        'JAVA_HOME': '/usr/lib/jvm/java-17-openjdk-amd64',
        'SPARK_HOME': '/opt/spark',
        'HADOOP_CONF_DIR': '/opt/spark/conf',
        'PYTHONPATH': '/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip',
    })

    # Créer la session Spark
    spark = SparkSession.builder \
        .appName("Verify MovieLens Data") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .config("spark.sql.catalogImplementation", "in-memory") \
        .getOrCreate()
    
    try:
        # Créer la base de données
        spark.sql("CREATE DATABASE IF NOT EXISTS movielens")
        spark.sql("USE movielens")
        
        # Créer les tables
        spark.sql("""
            CREATE TABLE IF NOT EXISTS movies (
                movieId INT,
                title STRING,
                genres STRING
            ) USING CSV OPTIONS (
                path 'hdfs://namenode:9000/user/airflow/movielens/movies.dat',
                delimiter '::',
                header 'false'
            )
        """)
        
        spark.sql("""
            CREATE TABLE IF NOT EXISTS ratings (
                userId INT,
                movieId INT,
                rating INT,
                timestamp BIGINT
            ) USING CSV OPTIONS (
                path 'hdfs://namenode:9000/user/airflow/movielens/ratings.dat',
                delimiter '::',
                header 'false'
            )
        """)
        
        spark.sql("""
            CREATE TABLE IF NOT EXISTS users (
                userId INT,
                gender STRING,
                age INT,
                occupation INT,
                zipcode STRING
            ) USING CSV OPTIONS (
                path 'hdfs://namenode:9000/user/airflow/movielens/users.dat',
                delimiter '::',
                header 'false'
            )
        """)
        
        # Exécuter les requêtes de vérification
        results = []
        
        results.append("Movies count:")
        movies_count = spark.sql("SELECT COUNT(*) as count FROM movies").collect()
        results.append(str(movies_count))
        
        results.append("\nRatings count:")
        ratings_count = spark.sql("SELECT COUNT(*) as count FROM ratings").collect()
        results.append(str(ratings_count))
        
        results.append("\nUsers count:")
        users_count = spark.sql("SELECT COUNT(*) as count FROM users").collect()
        results.append(str(users_count))
        
        results.append("\nSample movies:")
        movies_sample = spark.sql("SELECT * FROM movies LIMIT 5").collect()
        results.append(str(movies_sample))
        
        results.append("\nSample ratings:")
        ratings_sample = spark.sql("SELECT * FROM ratings LIMIT 5").collect()
        results.append(str(ratings_sample))
        
        results.append("\nSample users:")
        users_sample = spark.sql("SELECT * FROM users LIMIT 5").collect()
        results.append(str(users_sample))
        
        # Afficher les résultats
        output = "\n".join(results)
        logging.info(output)
        
        return {
            'returncode': 0,
            'stdout': output,
            'stderr': ''
        }
        
    finally:
        # Arrêter la session Spark
        spark.stop()

# Tâche pour télécharger les données
download_data = PythonOperator(
    task_id='download_movielens_data',
    python_callable=download_movielens_data,
    dag=dag,
)

# Tâche pour uploader les données vers HDFS
upload_data = PythonOperator(
    task_id='upload_to_hdfs',
    python_callable=upload_to_hdfs,
    dag=dag,
)

# Tâche pour vérifier les données
verify_data = PythonOperator(
    task_id='verify_data',
    python_callable=verify_data_task,
    dag=dag,
)

# Définition des dépendances
download_data >> upload_data >> verify_data 