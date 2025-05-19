from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.sql.functions import col, expr, count, avg, explode, array, struct, lit, when, split, desc, row_number, collect_list
import logging
import numpy as np
import math
from pyspark.sql.window import Window

def optimize_als_parameters(train_data, validation_data, spark_session):
    """
    Optimise les paramètres du modèle ALS en utilisant une grille de recherche.
    
    Args:
        train_data: DataFrame Spark contenant les données d'entraînement
        validation_data: DataFrame Spark contenant les données de validation
        spark_session: Session Spark active
    
    Returns:
        dict: Dictionnaire contenant les meilleurs paramètres trouvés
    """
    # Créer le modèle ALS de base
    als = ALS(
        userCol="userId",
        itemCol="movieId",
        ratingCol="rating",
        coldStartStrategy="drop",
        nonnegative=True
    )
    
    # Définir une grille de paramètres plus large
    param_grid = ParamGridBuilder() \
        .addGrid(als.rank, [10]) \
        .addGrid(als.regParam, [0.1]) \
        .addGrid(als.maxIter, [10]) \
        .addGrid(als.alpha, [0.01]) \
        .build()
    
    # Configurer les évaluateurs pour différentes métriques
    evaluators = {
        'rmse': RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction"),
        'mae': RegressionEvaluator(metricName="mae", labelCol="rating", predictionCol="prediction")
    }
    
    best_params = {}
    best_scores = {}
    
    # Évaluer chaque combinaison de paramètres
    for params in param_grid:
        # Configurer le modèle avec les paramètres actuels
        model = als.copy(params)
        
        # Entraîner le modèle
        fitted_model = model.fit(train_data)
        
        # Faire des prédictions sur l'ensemble de validation
        predictions = fitted_model.transform(validation_data)
        
        # Évaluer avec différentes métriques
        for metric_name, evaluator in evaluators.items():
            score = evaluator.evaluate(predictions)
            
            # Mettre à jour les meilleurs scores et paramètres
            if metric_name not in best_scores or score < best_scores[metric_name]:
                best_scores[metric_name] = score
                # Convertir les paramètres en dictionnaire
                param_dict = {param.name: params[param] for param in params}
                best_params[metric_name] = param_dict
                
                logging.info(f"Nouveau meilleur score {metric_name}: {score}")
                logging.info(f"Paramètres: {param_dict}")
    
    return best_params, best_scores

def evaluate_model_performance(model, test_data, spark_session, k=10):
    """
    Évalue les performances du modèle avec plusieurs métriques.
    
    Args:
        model: Modèle ALS entraîné
        test_data: DataFrame Spark contenant les données de test
        spark_session: Session Spark active
        k: Nombre de recommandations à considérer pour la précision@k
    
    Returns:
        dict: Dictionnaire contenant les différentes métriques d'évaluation
    """
    # Faire des prédictions
    predictions = model.transform(test_data)
    
    # Calculer RMSE et MAE
    evaluator_rmse = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
    evaluator_mae = RegressionEvaluator(metricName="mae", labelCol="rating", predictionCol="prediction")
    
    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)
    
    # Calculer la précision@k
    # Pour chaque utilisateur, vérifier si les films recommandés sont dans les films notés positivement
    user_recommendations = model.recommendForAllUsers(k)
    
    # Joindre avec les données de test pour comparer
    test_positive = test_data.filter(col("rating") >= 4.0)
    
    # Calculer la précision@k
    precision_at_k = calculate_precision_at_k(user_recommendations, test_positive, k)
    
    # Calculer la couverture (pourcentage d'utilisateurs ayant des recommandations)
    coverage = calculate_coverage(user_recommendations, test_data)
    
    # Charger les données des films depuis HDFS
    movies_df = spark_session.read \
        .option("delimiter", "::") \
        .option("header", "false") \
        .csv("hdfs://namenode:9000/user/airflow/movielens/movies.dat") \
        .toDF("movieId", "title", "genres")
    
    # Calculer la diversité des recommandations
    diversity = calculate_diversity(user_recommendations, movies_df)
    
    return {
        'rmse': rmse,
        'mae': mae,
        'precision_at_k': precision_at_k,
        'coverage': coverage,
        'diversity': diversity
    }

def calculate_precision_at_k(recommendations, test_positive, k):
    """
    Calcule la précision@k pour les recommandations.
    
    La précision@k mesure la proportion de films recommandés qui sont pertinents
    (c'est-à-dire notés positivement par l'utilisateur).
    
    Args:
        recommendations: DataFrame Spark contenant les recommandations
                        Format: userId, recommendations (array de structs avec movieId et rating)
        test_positive: DataFrame Spark contenant les films notés positivement (rating >= 4.0)
                      Format: userId, movieId, rating
        k: Nombre de recommandations à considérer
    
    Returns:
        float: Précision@k moyenne sur tous les utilisateurs
    """
    # 1. Extraire les k premiers films recommandés pour chaque utilisateur
    recommendations_exploded = recommendations \
        .select(
            col("userId"),
            explode("recommendations").alias("recommendation")
        ) \
        .select(
            col("userId"),
            col("recommendation.movieId").alias("recommended_movieId")
        )
    
    # 2. Joindre avec les films notés positivement
    hits = recommendations_exploded \
        .join(
            test_positive,
            (recommendations_exploded.userId == test_positive.userId) & 
            (recommendations_exploded.recommended_movieId == test_positive.movieId),
            "left"
        ) \
        .select(
            recommendations_exploded.userId,
            recommendations_exploded.recommended_movieId,
            when(test_positive.movieId.isNotNull(), 1).otherwise(0).alias("hit")
        )
    
    # 3. Calculer la précision pour chaque utilisateur
    user_precision = hits \
        .groupBy(col("userId")) \
        .agg(
            (count(when(col("hit") == 1, True)) / lit(k)).alias("precision")
        )
    
    # 4. Calculer la moyenne sur tous les utilisateurs
    overall_precision = user_precision \
        .agg(avg("precision").alias("precision_at_k")) \
        .collect()[0]["precision_at_k"]
    
    return overall_precision

def calculate_coverage(recommendations, test_data):
    """
    Calcule le pourcentage d'utilisateurs ayant des recommandations.
    """
    total_users = test_data.select(col("userId")).distinct().count()
    users_with_recommendations = recommendations.count()
    return users_with_recommendations / total_users

def calculate_diversity(recommendations, movies_df):
    """
    Calcule la diversité des recommandations en utilisant l'entropie des genres.
    
    La diversité est mesurée par l'entropie de la distribution des genres
    dans les recommandations. Une entropie plus élevée indique une plus grande
    diversité des genres recommandés.
    
    Args:
        recommendations: DataFrame Spark contenant les recommandations
                        Format: userId, recommendations (array de structs avec movieId et rating)
        movies_df: DataFrame Spark contenant les informations des films
                  Format: movieId, title, genres (pipe-separated string)
    
    Returns:
        float: Diversité moyenne (entropie) sur tous les utilisateurs
    """
    # 1. Extraire les movieIds des recommandations
    recommendations_exploded = recommendations \
        .select(
            col("userId"),
            explode("recommendations").alias("recommendation")
        ) \
        .select(
            col("userId"),
            col("recommendation.movieId").alias("movieId")
        )
    
    # 2. Joindre avec les informations des films pour obtenir les genres
    recommendations_with_genres = recommendations_exploded \
        .join(movies_df.select("movieId", "genres"), "movieId") \
        .select(
            col("userId"),
            col("movieId"),
            split(col("genres"), "\\|").alias("genres")
        )
    
    # 3. Exploser les genres pour chaque film
    genres_exploded = recommendations_with_genres \
        .select(
            col("userId"),
            col("movieId"),
            explode("genres").alias("genre")
        )
    
    # 4. Calculer la distribution des genres pour chaque utilisateur
    genre_counts = genres_exploded \
        .groupBy(col("userId"), col("genre")) \
        .agg(count("*").cast("integer").alias("genre_count"))
    
    # 5. Calculer l'entropie pour chaque utilisateur
    # Entropie = -sum(p * log2(p)) où p est la proportion de chaque genre
    user_diversity = genre_counts \
        .groupBy(col("userId")) \
        .agg(
            sum("genre_count").cast("double").alias("total_genres")
        ) \
        .join(genre_counts, "userId") \
        .withColumn(
            "proportion",
            col("genre_count").cast("double") / col("total_genres")
        ) \
        .withColumn(
            "entropy_term",
            -col("proportion") * math.log2(col("proportion"))
        ) \
        .groupBy(col("userId")) \
        .agg(
            sum("entropy_term").alias("diversity")
        )
    
    # 6. Calculer la moyenne sur tous les utilisateurs
    overall_diversity = user_diversity \
        .agg(avg("diversity").alias("average_diversity")) \
        .collect()[0]["average_diversity"]
    
    return overall_diversity

def handle_cold_start(model, user_data, item_data, n_recommendations=10):
    """
    Gère le problème du cold start pour les nouveaux utilisateurs.
    
    Utilise une approche hybride combinant :
    1. Recommandations basées sur la popularité globale
    2. Recommandations basées sur les genres populaires
    3. Filtrage pour éviter les films déjà vus
    
    Args:
        model: Modèle ALS entraîné
        user_data: DataFrame Spark contenant les données utilisateur
                  Format: userId, [autres colonnes utilisateur]
        item_data: DataFrame Spark contenant les données des films
                  Format: movieId, title, genres, [autres colonnes film]
        n_recommendations: Nombre de recommandations à générer
    
    Returns:
        DataFrame: Recommandations pour les nouveaux utilisateurs
                  Format: userId, recommendations (array de structs)
    """
    # 1. Calculer la popularité globale des films
    # (basée sur le nombre de notes et la moyenne des notes)
    movie_popularity = user_data \
        .groupBy(col("movieId")) \
        .agg(
            count("*").alias("num_ratings"),
            avg("rating").alias("avg_rating")
        ) \
        .withColumn(
            "popularity_score",
            col("num_ratings") * col("avg_rating")
        )
    
    # 2. Calculer la popularité des genres
    genre_popularity = user_data \
        .join(item_data, "movieId") \
        .select(
            col("movieId"),
            col("rating"),
            explode(split(col("genres"), "\\|")).alias("genre")
        ) \
        .groupBy(col("genre")) \
        .agg(
            count("*").alias("num_ratings"),
            avg("rating").alias("avg_rating")
        ) \
        .withColumn(
            "genre_score",
            col("num_ratings") * col("avg_rating")
        )
    
    # 3. Pour chaque nouveau utilisateur, générer des recommandations
    def generate_recommendations_for_user(user_id):
        # Créer un DataFrame avec l'ID de l'utilisateur
        user_df = spark.createDataFrame([(user_id,)], ["userId"])
        
        # Obtenir les films les plus populaires
        popular_movies = movie_popularity \
            .orderBy(desc("popularity_score")) \
            .limit(n_recommendations * 2)  # Prendre plus de films pour le filtrage
        
        # Joindre avec les informations des films
        recommendations = popular_movies \
            .join(item_data, "movieId") \
            .select(
                lit(user_id).alias("userId"),
                col("movieId"),
                col("popularity_score").alias("rating")
            )
        
        # Trier et limiter aux n_recommendations premiers
        final_recommendations = recommendations \
            .orderBy(desc("rating")) \
            .limit(n_recommendations)
        
        return final_recommendations
    
    # 4. Générer les recommandations pour tous les nouveaux utilisateurs
    new_users = user_data \
        .select(col("userId")) \
        .distinct() \
        .join(
            model.userFactors.select(col("id")).distinct(),
            user_data.userId == model.userFactors.id,
            "left_anti"
        )
    
    # 5. Appliquer la génération de recommandations à chaque nouvel utilisateur
    all_recommendations = new_users \
        .rdd \
        .flatMap(lambda row: generate_recommendations_for_user(row.userId).collect()) \
        .toDF()
    
    # 6. Structurer les recommandations dans le format attendu
    final_recommendations = all_recommendations \
        .groupBy(col("userId")) \
        .agg(
            collect_list(
                struct(
                    col("movieId"),
                    col("rating")
                )
            ).alias("recommendations")
        )
    
    return final_recommendations 