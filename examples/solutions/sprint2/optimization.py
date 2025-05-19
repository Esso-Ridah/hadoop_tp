from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def optimize_als_parameters(spark, train_data, validation_data):
    """
    Optimise les paramètres du modèle ALS en utilisant la validation croisée.
    
    Args:
        spark: Session Spark active
        train_data: DataFrame Spark pour l'entraînement
        validation_data: DataFrame Spark pour la validation
    
    Returns:
        dict: Meilleurs paramètres trouvés
    """
    # Créer le modèle ALS de base
    als = ALS(
        userCol="userId",
        itemCol="movieId",
        ratingCol="rating",
        coldStartStrategy="drop",
        nonnegative=True
    )
    
    # Définir la grille de paramètres
    param_grid = ParamGridBuilder() \
        .addGrid(als.rank, [10, 50, 100]) \
        .addGrid(als.regParam, [0.01, 0.05, 0.1]) \
        .addGrid(als.maxIter, [10, 20]) \
        .addGrid(als.alpha, [0.01, 0.1, 1.0]) \
        .build()
    
    # Configurer l'évaluateur
    evaluator = RegressionEvaluator(
        metricName="rmse",
        labelCol="rating",
        predictionCol="prediction"
    )
    
    # Configurer la validation croisée
    cv = CrossValidator(
        estimator=als,
        estimatorParamMaps=param_grid,
        evaluator=evaluator,
        numFolds=3,
        parallelism=2
    )
    
    # Entraîner le modèle
    cv_model = cv.fit(train_data)
    
    # Récupérer les résultats de la validation croisée
    cv_results = []
    for i, param_map in enumerate(param_grid):
        avg_metrics = cv_model.avgMetrics[i]
        params = {param.name: value for param, value in param_map.items()}
        cv_results.append({
            "rank": params.get("rank"),
            "regParam": params.get("regParam"),
            "maxIter": params.get("maxIter"),
            "alpha": params.get("alpha"),
            "rmse": avg_metrics
        })
    
    # Convertir en DataFrame pandas pour l'analyse
    results_df = pd.DataFrame(cv_results)
    
    # Visualiser les résultats
    plt.figure(figsize=(15, 10))
    
    # 1. Impact du rank
    plt.subplot(2, 2, 1)
    sns.boxplot(x="rank", y="rmse", data=results_df)
    plt.title("Impact du Rank sur le RMSE")
    
    # 2. Impact du regParam
    plt.subplot(2, 2, 2)
    sns.boxplot(x="regParam", y="rmse", data=results_df)
    plt.title("Impact du RegParam sur le RMSE")
    
    # 3. Impact du maxIter
    plt.subplot(2, 2, 3)
    sns.boxplot(x="maxIter", y="rmse", data=results_df)
    plt.title("Impact du MaxIter sur le RMSE")
    
    # 4. Impact de l'alpha
    plt.subplot(2, 2, 4)
    sns.boxplot(x="alpha", y="rmse", data=results_df)
    plt.title("Impact de l'Alpha sur le RMSE")
    
    plt.tight_layout()
    plt.savefig("parameter_optimization.png")
    plt.close()
    
    # Trouver les meilleurs paramètres
    best_params = {
        "rank": cv_model.bestModel.rank,
        "regParam": cv_model.bestModel._java_obj.parent().getRegParam(),
        "maxIter": cv_model.bestModel._java_obj.parent().getMaxIter(),
        "alpha": cv_model.bestModel._java_obj.parent().getAlpha()
    }
    
    # Évaluer le meilleur modèle sur l'ensemble de validation
    best_model = cv_model.bestModel
    predictions = best_model.transform(validation_data)
    rmse = evaluator.evaluate(predictions)
    
    return {
        "best_params": best_params,
        "best_rmse": rmse,
        "cv_results": results_df
    }

def analyze_optimization_results(results):
    """
    Analyse les résultats de l'optimisation des paramètres.
    
    Args:
        results: Résultats de l'optimisation
    
    Returns:
        dict: Analyse des résultats
    """
    # Analyser l'impact de chaque paramètre
    param_analysis = {}
    
    for param in ["rank", "regParam", "maxIter", "alpha"]:
        param_stats = results["cv_results"].groupby(param)["rmse"].agg(["mean", "std", "min", "max"])
        param_analysis[param] = param_stats
    
    # Identifier les tendances
    trends = {
        "rank": "Impact sur la capacité du modèle à capturer des relations complexes",
        "regParam": "Impact sur la régularisation et le surapprentissage",
        "maxIter": "Impact sur la convergence et le temps d'entraînement",
        "alpha": "Impact sur la confiance dans les observations"
    }
    
    return {
        "parameter_analysis": param_analysis,
        "trends": trends,
        "best_configuration": results["best_params"],
        "best_performance": results["best_rmse"]
    }

if __name__ == "__main__":
    # Créer la session Spark
    spark = SparkSession.builder \
        .appName("Movie Recommendation - Parameter Optimization") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    try:
        # Charger les données
        ratings_df = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/ratings_clean.parquet")
        
        # Diviser en ensembles d'entraînement, validation et test
        train, validation, test = ratings_df.randomSplit([0.6, 0.2, 0.2], seed=42)
        
        # Optimiser les paramètres
        results = optimize_als_parameters(spark, train, validation)
        
        # Analyser les résultats
        analysis = analyze_optimization_results(results)
        
        # Afficher les résultats
        print("\nMeilleure configuration:")
        for param, value in results["best_params"].items():
            print(f"{param}: {value}")
        
        print(f"\nMeilleur RMSE: {results['best_rmse']}")
        
        print("\nAnalyse des paramètres:")
        for param, stats in analysis["parameter_analysis"].items():
            print(f"\n{param}:")
            print(stats)
            print(f"Tendance: {analysis['trends'][param]}")
        
    finally:
        spark.stop() 