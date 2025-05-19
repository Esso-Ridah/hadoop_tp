from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, desc
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def analyze_data(spark):
    """
    Analyse les données du jeu de données MovieLens.
    
    Args:
        spark: Session Spark active
    
    Returns:
        dict: Dictionnaire contenant les statistiques principales
    """
    # Charger les données
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
    
    # 1. Distribution des notes
    rating_dist = ratings_df \
        .groupBy("rating") \
        .agg(count("*").alias("count")) \
        .orderBy("rating")
    
    # Convertir en pandas pour la visualisation
    rating_dist_pd = rating_dist.toPandas()
    
    # Créer le graphique
    plt.figure(figsize=(10, 6))
    sns.barplot(x="rating", y="count", data=rating_dist_pd)
    plt.title("Distribution des Notes")
    plt.xlabel("Note")
    plt.ylabel("Nombre de notes")
    plt.savefig("rating_distribution.png")
    plt.close()
    
    # 2. Utilisateurs les plus actifs
    active_users = ratings_df \
        .groupBy("userId") \
        .agg(count("*").alias("num_ratings")) \
        .orderBy(desc("num_ratings")) \
        .limit(10)
    
    # 3. Films les plus notés
    popular_movies = ratings_df \
        .groupBy("movieId") \
        .agg(
            count("*").alias("num_ratings"),
            avg("rating").alias("avg_rating")
        ) \
        .join(movies_df, "movieId") \
        .orderBy(desc("num_ratings")) \
        .limit(10)
    
    # 4. Statistiques générales
    stats = {
        "total_ratings": ratings_df.count(),
        "unique_users": ratings_df.select("userId").distinct().count(),
        "unique_movies": ratings_df.select("movieId").distinct().count(),
        "avg_rating": ratings_df.select(avg("rating")).collect()[0][0],
        "sparsity": 1 - (ratings_df.count() / 
                        (ratings_df.select("userId").distinct().count() * 
                         ratings_df.select("movieId").distinct().count()))
    }
    
    # 5. Distribution des genres
    genre_dist = movies_df \
        .select("genres") \
        .rdd \
        .flatMap(lambda x: x[0].split("|")) \
        .map(lambda x: (x, 1)) \
        .reduceByKey(lambda x, y: x + y) \
        .toDF(["genre", "count"]) \
        .orderBy(desc("count"))
    
    # Convertir en pandas pour la visualisation
    genre_dist_pd = genre_dist.toPandas()
    
    # Créer le graphique
    plt.figure(figsize=(12, 6))
    sns.barplot(x="genre", y="count", data=genre_dist_pd)
    plt.title("Distribution des Genres")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("genre_distribution.png")
    plt.close()
    
    return {
        "stats": stats,
        "active_users": active_users.toPandas(),
        "popular_movies": popular_movies.toPandas(),
        "rating_distribution": rating_dist_pd,
        "genre_distribution": genre_dist_pd
    }

if __name__ == "__main__":
    # Créer la session Spark
    spark = SparkSession.builder \
        .appName("Movie Recommendation - Data Analysis") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    try:
        # Exécuter l'analyse
        results = analyze_data(spark)
        
        # Afficher les statistiques
        print("\nStatistiques générales:")
        for key, value in results["stats"].items():
            print(f"{key}: {value}")
        
        print("\nTop 10 utilisateurs les plus actifs:")
        print(results["active_users"])
        
        print("\nTop 10 films les plus populaires:")
        print(results["popular_movies"])
        
    finally:
        spark.stop() 