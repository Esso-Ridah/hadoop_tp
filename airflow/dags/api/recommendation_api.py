from flask import Flask, jsonify, request
from pyspark.sql import SparkSession
from prometheus_client import Counter, Histogram, start_http_server
import time
import logging
from functools import wraps

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Métriques Prometheus
recommendation_counter = Counter('recommendations_total', 'Nombre total de recommandations générées')
response_time = Histogram('response_time_seconds', 'Temps de réponse des requêtes')
error_counter = Counter('errors_total', 'Nombre total d\'erreurs')

# Décorateur pour mesurer le temps de réponse
def track_time(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            response_time.observe(time.time() - start_time)
            return result
        except Exception as e:
            error_counter.inc()
            logger.error(f"Erreur: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return decorated_function

def get_spark_session():
    """Crée ou récupère une session Spark"""
    return SparkSession.builder \
        .appName("RecommendationAPI") \
        .master("spark://spark-master:7077") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.host", "recommendation-api") \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .getOrCreate()

@app.route('/recommendations/<int:user_id>', methods=['GET'])
@track_time
def get_recommendations(user_id):
    """Endpoint pour obtenir les recommandations d'un utilisateur"""
    try:
        spark = get_spark_session()
        
        # Lecture des recommandations depuis HDFS
        recommendations_df = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/recommendations")
        
        # Filtrage pour l'utilisateur spécifié
        user_recommendations = recommendations_df.filter(f"userId = {user_id}")
        
        # Conversion en liste de dictionnaires
        recommendations = user_recommendations.collect()
        
        # Incrémentation du compteur de recommandations
        recommendation_counter.inc(len(recommendations))
        
        return jsonify({
            "user_id": user_id,
            "recommendations": [{
                "movieId": row.movieId,
                "title": row.title,
                "score": row.score
            } for row in recommendations]
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des recommandations: {str(e)}")
        error_counter.inc()
        return jsonify({"error": str(e)}), 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Endpoint pour obtenir les métriques du système"""
    try:
        spark = get_spark_session()
        
        # Lecture des statistiques depuis HDFS
        stats_df = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/stats")
        
        # Conversion en dictionnaire
        stats = stats_df.collect()[0].asDict()
        
        return jsonify({
            "total_recommendations": recommendation_counter._value.get(),
            "average_response_time": response_time._sum.get() / response_time._count.get() if response_time._count.get() > 0 else 0,
            "error_rate": error_counter._value.get() / (recommendation_counter._value.get() + error_counter._value.get()) if (recommendation_counter._value.get() + error_counter._value.get()) > 0 else 0,
            "system_stats": stats
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint pour vérifier l'état du service"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Démarrage du serveur de métriques Prometheus
    start_http_server(8000)
    # Démarrage de l'API Flask
    app.run(host='0.0.0.0', port=5000) 