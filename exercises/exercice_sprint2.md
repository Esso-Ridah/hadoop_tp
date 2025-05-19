
# Sprint 2 : Optimisation des Paramètres (Optionnel)

## Objectifs
L'objectif de ce sprint est d'optimiser les paramètres du modèle ALS (Alternating Least Squares) pour améliorer la qualité des recommandations. Vous allez utiliser la validation croisée et l'analyse des performances pour trouver les meilleurs hyperparamètres.

## Exercices

### 1. Validation Croisée
- Implémenter une validation croisée pour le modèle ALS
- Diviser les données en k-folds (k=3 ou 5)
- Évaluer le modèle sur chaque fold
- Calculer les métriques moyennes

### 2. Optimisation des Hyperparamètres
Tester différentes combinaisons de paramètres :
- `rank` : [10, 50, 100] (nombre de facteurs latents)
- `regParam` : [0.01, 0.05, 0.1] (paramètre de régularisation)
- `maxIter` : [10, 20] (nombre d'itérations)
- `alpha` : [0.01, 0.1, 1.0] (paramètre de confiance)

### 3. Analyse des Performances
Pour chaque combinaison de paramètres :
- Calculer le RMSE (Root Mean Square Error)
- Mesurer le temps d'entraînement
- Évaluer la diversité des recommandations
- Analyser la distribution des prédictions

### 4. Visualisation des Résultats
Créer des visualisations pour :
- Impact de chaque paramètre sur le RMSE
- Temps d'entraînement vs performance
- Distribution des prédictions
- Comparaison des recommandations

## Livrables Attendus

1. **Code Source**
   - Script d'optimisation des paramètres
   - Fonctions de validation croisée
   - Code de visualisation
   - Tests unitaires

2. **Documentation**
   - Description de la méthodologie
   - Analyse des résultats
   - Graphiques et visualisations
   - Recommandations finales

3. **Présentation**
   - Résultats de l'optimisation
   - Impact des paramètres
   - Améliorations obtenues
   - Limitations identifiées

## Critères d'Évaluation

1. **Qualité du Code** (30%)
   - Structure et organisation
   - Documentation
   - Gestion des erreurs
   - Tests unitaires

2. **Méthodologie** (30%)
   - Approche de validation croisée
   - Choix des paramètres
   - Analyse des résultats
   - Visualisations

3. **Résultats** (40%)
   - Amélioration des performances
   - Qualité des recommandations
   - Temps de traitement
   - Documentation des résultats

## Conseils d'Implémentation

1. **Validation Croisée**
   ```python
   from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
   from pyspark.ml.evaluation import RegressionEvaluator
   
   # Créer la grille de paramètres
   param_grid = ParamGridBuilder() \
       .addGrid(als.rank, [10, 50, 100]) \
       .addGrid(als.regParam, [0.01, 0.05, 0.1]) \
       .build()
   
   # Configurer la validation croisée
   cv = CrossValidator(
       estimator=als,
       estimatorParamMaps=param_grid,
       evaluator=evaluator,
       numFolds=3
   )
   ```

2. **Évaluation des Performances**
   ```python
   # Calculer le RMSE
   evaluator = RegressionEvaluator(
       metricName="rmse",
       labelCol="rating",
       predictionCol="prediction"
   )
   
   # Mesurer le temps
   import time
   start_time = time.time()
   # ... entraînement du modèle ...
   training_time = time.time() - start_time
   ```

3. **Visualisation**
   ```python
   import matplotlib.pyplot as plt
   import seaborn as sns
   
   # Créer un graphique pour chaque paramètre
   plt.figure(figsize=(10, 6))
   sns.boxplot(x="rank", y="rmse", data=results_df)
   plt.title("Impact du Rank sur le RMSE")
   plt.savefig("rank_impact.png")
   ```

## Ressources

1. **Documentation**
   - [Spark ML Tuning](https://spark.apache.org/docs/latest/ml-tuning.html)
   - [ALS Documentation](https://spark.apache.org/docs/latest/ml-collaborative-filtering.html)
   - [Cross-Validation Guide](https://spark.apache.org/docs/latest/ml-tuning.html#cross-validation)

2. **Exemples**
   - Voir `/examples/solutions/sprint2/optimization.py`
   - Étudier les visualisations fournies
   - Analyser les patterns d'implémentation

## Questions Fréquentes

1. **Comment choisir les valeurs des paramètres ?**
   - Commencer avec des plages larges
   - Affiner progressivement
   - Considérer les contraintes de ressources

2. **Quelle métrique utiliser ?**
   - RMSE pour la précision
   - Temps d'entraînement pour l'efficacité
   - Diversité pour la qualité des recommandations

3. **Comment gérer les ressources ?**
   - Utiliser le caching Spark
   - Optimiser les partitions
   - Surveiller l'utilisation mémoire

## Prochaines Étapes

Après avoir complété ce sprint, vous pourrez :
1. Implémenter les améliorations du Sprint 3
2. Ajouter des fonctionnalités de monitoring
3. Développer l'interface utilisateur 