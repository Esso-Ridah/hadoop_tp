from flask import Flask, jsonify, request
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, desc
import logging
import time
import json
from datetime import datetime
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Métriques Prometheus
REQUEST_COUNT = Counter(
    'recommendation_requests_total',
    'Total number of recommendation requests',
    ['endpoint']
)
REQUEST_LATENCY = Histogram(
    'recommendation_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)
RECOMMENDATION_COUNT = Gauge(
    'recommendations_generated_total',
    'Total number of recommendations generated'
)
MODEL_PERFORMANCE = Gauge(
    'model_performance_rmse',
    'Current RMSE of the recommendation model'
)

app = Flask(__name__)

def get_spark_session():
    """Crée et retourne une session Spark."""
    return SparkSession.builder \
        .appName("Movie Recommendation - API") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()

def load_recommendations(spark):
    """Charge les recommandations depuis HDFS."""
    return spark.read.parquet(
        "hdfs://namenode:9000/user/airflow/movielens/improved_recommendations.parquet"
    )

def get_user_recommendations(spark, user_id, n_recommendations=10):
    """Récupère les recommandations pour un utilisateur spécifique."""
    recommendations_df = load_recommendations(spark)
    
    user_recs = recommendations_df \
        .filter(col("userId") == user_id) \
        .select("recommendations") \
        .collect()
    
    if not user_recs:
        return []
    
    return user_recs[0].recommendations[:n_recommendations]

def get_system_metrics(spark):
    """Récupère les métriques du système."""
    recommendations_df = load_recommendations(spark)
    
    metrics = {
        "total_users": recommendations_df.count(),
        "total_recommendations": recommendations_df \
            .select(explode("recommendations")) \
            .count(),
        "avg_recommendations_per_user": recommendations_df \
            .select(size("recommendations").alias("rec_count")) \
            .agg(avg("rec_count")) \
            .collect()[0][0]
    }
    
    return metrics

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
@REQUEST_LATENCY.labels(endpoint='/api/recommendations').time()
def get_recommendations(user_id):
    """Endpoint pour récupérer les recommandations d'un utilisateur."""
    REQUEST_COUNT.labels(endpoint='/api/recommendations').inc()
    
    try:
        spark = get_spark_session()
        recommendations = get_user_recommendations(spark, user_id)
        
        RECOMMENDATION_COUNT.inc(len(recommendations))
        
        return jsonify({
            "user_id": user_id,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        spark.stop()

@app.route('/api/metrics', methods=['GET'])
@REQUEST_LATENCY.labels(endpoint='/api/metrics').time()
def get_metrics():
    """Endpoint pour récupérer les métriques du système."""
    REQUEST_COUNT.labels(endpoint='/api/metrics').inc()
    
    try:
        spark = get_spark_session()
        metrics = get_system_metrics(spark)
        
        return jsonify({
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        spark.stop()

@app.route('/metrics', methods=['GET'])
def metrics():
    """Endpoint Prometheus pour les métriques."""
    return prometheus_client.generate_latest()

def update_model_performance(spark):
    """Met à jour les métriques de performance du modèle."""
    try:
        # Charger les données de test
        test_data = spark.read.parquet(
            "hdfs://namenode:9000/user/airflow/movielens/test_data.parquet"
        )
        
        # Charger le modèle
        model = ALSModel.load(
            "hdfs://namenode:9000/user/airflow/movielens/als_model"
        )
        
        # Calculer le RMSE
        predictions = model.transform(test_data)
        evaluator = RegressionEvaluator(
            metricName="rmse",
            labelCol="rating",
            predictionCol="prediction"
        )
        rmse = evaluator.evaluate(predictions)
        
        # Mettre à jour la métrique
        MODEL_PERFORMANCE.set(rmse)
        
        logger.info(f"Updated model performance metric: RMSE = {rmse}")
    except Exception as e:
        logger.error(f"Error updating model performance: {str(e)}")

if __name__ == '__main__':
    # Démarrer le serveur Prometheus
    prometheus_client.start_http_server(8000)
    
    # Mettre à jour les métriques de performance toutes les heures
    def update_metrics():
        while True:
            spark = get_spark_session()
            try:
                update_model_performance(spark)
            finally:
                spark.stop()
            time.sleep(3600)  # Attendre une heure
    
    import threading
    metrics_thread = threading.Thread(target=update_metrics)
    metrics_thread.daemon = True
    metrics_thread.start()
    
    # Démarrer l'application Flask
    app.run(host='0.0.0.0', port=5000) 