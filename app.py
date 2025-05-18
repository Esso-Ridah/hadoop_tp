from flask import Flask, render_template, jsonify
from pyspark.sql import SparkSession
import os

app = Flask(__name__)

def get_spark_session():
    return SparkSession.builder \
        .appName("Movie Recommendation Viewer") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommendations/<int:user_id>')
def get_recommendations(user_id):
    spark = get_spark_session()
    
    # Charger les recommandations
    recommendations = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/recommendations.parquet")
    
    # Charger les informations des films
    movies = spark.read \
        .option("delimiter", "::") \
        .option("header", "false") \
        .csv("hdfs://namenode:9000/user/airflow/movielens/movies.dat") \
        .toDF("movieId", "title", "genres")
    
    # Filtrer les recommandations pour l'utilisateur
    user_recommendations = recommendations.filter(f"userId = {user_id}")
    
    # Joindre avec les informations des films
    result = user_recommendations \
        .select("userId", "recommendations") \
        .collect()
    
    if not result:
        return jsonify({"error": "User not found"}), 404
    
    # Extraire les recommandations
    recommendations_list = []
    for rec in result[0].recommendations:
        movie_info = movies.filter(f"movieId = {rec.movieId}").collect()
        if movie_info:
            recommendations_list.append({
                "movieId": rec.movieId,
                "title": movie_info[0].title,
                "genres": movie_info[0].genres,
                "rating": rec.rating
            })
    
    return jsonify(recommendations_list)

@app.route('/api/users')
def get_users():
    spark = get_spark_session()
    
    # Charger les recommandations
    recommendations = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/recommendations.parquet")
    
    # Obtenir la liste des utilisateurs
    users = recommendations.select("userId").distinct().collect()
    
    return jsonify([user.userId for user in users])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 