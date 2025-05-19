from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, count, avg, desc, lit, when
from pyspark.ml.recommendation import ALS, ALSModel
import math

def handle_cold_start(spark, model, user_data, item_data, n_recommendations=10):
    """
    Gère le problème du cold start pour les nouveaux utilisateurs.
    
    Args:
        spark: Session Spark active
        model: Modèle ALS entraîné
        user_data: DataFrame des données utilisateur
        item_data: DataFrame des données des films
        n_recommendations: Nombre de recommandations à générer
    
    Returns:
        DataFrame: Recommandations pour les nouveaux utilisateurs
    """
    # Calculer la popularité globale des films
    movie_popularity = user_data \
        .groupBy("movieId") \
        .agg(
            count("*").alias("num_ratings"),
            avg("rating").alias("avg_rating")
        ) \
        .withColumn(
            "popularity_score",
            col("num_ratings") * col("avg_rating")
        )
    
    # Calculer la popularité des genres
    genre_popularity = user_data \
        .join(item_data, "movieId") \
        .select(
            col("movieId"),
            col("rating"),
            explode(split(col("genres"), "\\|")).alias("genre")
        ) \
        .groupBy("genre") \
        .agg(
            count("*").alias("num_ratings"),
            avg("rating").alias("avg_rating")
        ) \
        .withColumn(
            "genre_score",
            col("num_ratings") * col("avg_rating")
        )
    
    # Identifier les nouveaux utilisateurs
    new_users = user_data \
        .select("userId") \
        .distinct() \
        .join(
            model.userFactors.select("id").distinct(),
            user_data.userId == model.userFactors.id,
            "left_anti"
        )
    
    # Générer des recommandations basées sur la popularité
    recommendations = new_users \
        .crossJoin(
            movie_popularity \
                .join(item_data, "movieId") \
                .orderBy(desc("popularity_score")) \
                .limit(n_recommendations * 2)
        ) \
        .select(
            col("userId"),
            col("movieId"),
            col("title"),
            col("genres"),
            col("popularity_score").alias("rating")
        ) \
        .orderBy("userId", desc("rating")) \
        .groupBy("userId") \
        .agg(
            collect_list(
                struct(
                    col("movieId"),
                    col("title"),
                    col("genres"),
                    col("rating")
                )
            ).alias("recommendations")
        )
    
    return recommendations

def enhance_diversity(recommendations, movies_df, k=10):
    """
    Améliore la diversité des recommandations.
    
    Args:
        recommendations: DataFrame des recommandations
        movies_df: DataFrame des films
        k: Nombre de recommandations à considérer
    
    Returns:
        DataFrame: Recommandations diversifiées
    """
    # Extraire les genres des films recommandés
    recommendations_with_genres = recommendations \
        .select(
            col("userId"),
            explode("recommendations").alias("recommendation")
        ) \
        .select(
            col("userId"),
            col("recommendation.movieId").alias("movieId")
        ) \
        .join(movies_df, "movieId") \
        .select(
            col("userId"),
            col("movieId"),
            explode(split(col("genres"), "\\|")).alias("genre")
        )
    
    # Calculer la diversité pour chaque utilisateur
    user_diversity = recommendations_with_genres \
        .groupBy("userId", "genre") \
        .agg(count("*").alias("genre_count")) \
        .groupBy("userId") \
        .agg(
            sum("genre_count").alias("total_genres"),
            collect_list(
                struct(
                    col("genre"),
                    col("genre_count")
                )
            ).alias("genre_distribution")
        )
    
    # Calculer l'entropie pour chaque utilisateur
    def calculate_entropy(genre_dist):
        total = sum(g.genre_count for g in genre_dist)
        probs = [g.genre_count / total for g in genre_dist]
        return -sum(p * math.log2(p) for p in probs)
    
    # Appliquer la fonction d'entropie
    user_diversity = user_diversity \
        .withColumn(
            "diversity_score",
            udf(calculate_entropy, DoubleType())("genre_distribution")
        )
    
    return user_diversity

def personalize_recommendations(recommendations, user_preferences, k=10):
    """
    Personnalise les recommandations en fonction des préférences utilisateur.
    
    Args:
        recommendations: DataFrame des recommandations
        user_preferences: DataFrame des préférences utilisateur
        k: Nombre de recommandations à considérer
    
    Returns:
        DataFrame: Recommandations personnalisées
    """
    # Joindre les recommandations avec les préférences utilisateur
    personalized_recommendations = recommendations \
        .join(user_preferences, "userId") \
        .select(
            col("userId"),
            explode("recommendations").alias("recommendation")
        ) \
        .select(
            col("userId"),
            col("recommendation.movieId").alias("movieId"),
            col("recommendation.rating").alias("base_rating"),
            col("preferred_genres")
        )
    
    # Calculer le score personnalisé
    def calculate_personalized_score(base_rating, movie_genres, preferred_genres):
        # Vérifier le chevauchement des genres
        movie_genre_set = set(movie_genres.split("|"))
        preferred_genre_set = set(preferred_genres)
        overlap = len(movie_genre_set.intersection(preferred_genre_set))
        
        # Ajuster le score en fonction du chevauchement
        return base_rating * (1 + 0.1 * overlap)
    
    # Appliquer la fonction de score
    personalized_recommendations = personalized_recommendations \
        .withColumn(
            "personalized_score",
            udf(calculate_personalized_score, DoubleType())(
                "base_rating",
                "genres",
                "preferred_genres"
            )
        ) \
        .orderBy("userId", desc("personalized_score")) \
        .groupBy("userId") \
        .agg(
            collect_list(
                struct(
                    col("movieId"),
                    col("personalized_score").alias("rating")
                )
            ).alias("recommendations")
        )
    
    return personalized_recommendations

if __name__ == "__main__":
    # Créer la session Spark
    spark = SparkSession.builder \
        .appName("Movie Recommendation - Improvements") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    try:
        # Charger les données
        ratings_df = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/ratings_clean.parquet")
        movies_df = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/movies_with_year.parquet")
        
        # Charger le modèle
        model = ALSModel.load("hdfs://namenode:9000/user/airflow/movielens/als_model")
        
        # Gérer le cold start
        cold_start_recommendations = handle_cold_start(
            spark,
            model,
            ratings_df,
            movies_df
        )
        
        # Améliorer la diversité
        diverse_recommendations = enhance_diversity(
            cold_start_recommendations,
            movies_df
        )
        
        # Personnaliser les recommandations
        # (nécessite des données de préférences utilisateur)
        # personalized_recommendations = personalize_recommendations(
        #     diverse_recommendations,
        #     user_preferences_df
        # )
        
        # Sauvegarder les recommandations améliorées
        diverse_recommendations.write \
            .mode("overwrite") \
            .parquet("hdfs://namenode:9000/user/airflow/movielens/improved_recommendations.parquet")
        
    finally:
        spark.stop() 