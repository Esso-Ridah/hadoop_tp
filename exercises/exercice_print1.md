# Sprint 1 : Implémentation de Base du Système de Recommandation

## Objectif
Implémenter un système de recommandation basique utilisant l'algorithme ALS (Alternating Least Squares) de Spark MLlib.

## Contexte
Le DAG `movie_recommendation.py` fournit une base fonctionnelle pour le système de recommandation. Votre tâche est d'améliorer et d'optimiser ce système.

## Exercices

### 1. Analyse des Données (2 points)
- Analyser la distribution des notes dans le jeu de données
- Identifier les utilisateurs et films les plus actifs
- Visualiser les résultats avec des graphiques appropriés

**Code à compléter :**
```python
def analyze_data(spark):
    # TODO: Implémenter l'analyse des données
    pass
```

### 2. Optimisation des Paramètres ALS (3 points)
- Tester différentes combinaisons de paramètres pour ALS
- Évaluer l'impact de chaque paramètre sur les performances
- Documenter les résultats et justifier les choix

**Paramètres à optimiser :**
- `rank` : dimension des facteurs latents
- `regParam` : paramètre de régularisation
- `maxIter` : nombre maximum d'itérations
- `alpha` : paramètre de confiance

### 3. Évaluation des Performances (3 points)
- Implémenter des métriques d'évaluation supplémentaires
  - MAE (Mean Absolute Error)
  - Précision@k
  - Rappel@k
- Comparer les performances avec différentes configurations
- Analyser les erreurs de prédiction

**Code à compléter :**
```python
def evaluate_model(predictions, k=10):
    # TODO: Implémenter les métriques d'évaluation
    pass
```

### 4. Amélioration des Recommandations (2 points)
- Filtrer les films déjà vus par l'utilisateur
- Ajouter des informations sur les films (titre, genre) aux recommandations
- Implémenter une fonction de diversité des recommandations

**Code à compléter :**
```python
def enhance_recommendations(recommendations, movies_df):
    # TODO: Améliorer la qualité des recommandations
    pass
```

## Livrables Attendus

1. **Code Source**
   - Fichiers Python modifiés
   - Tests unitaires
   - Documentation du code

2. **Rapport Technique**
   - Analyse des données
   - Résultats des expérimentations
   - Choix d'optimisation
   - Métriques de performance

3. **Présentation**
   - Slides (max 10)
   - Démonstration du système
   - Réponses aux questions

## Critères d'Évaluation

- **Qualité du Code** (3 points)
  - Lisibilité et structure
  - Documentation
  - Tests unitaires

- **Performance du Modèle** (4 points)
  - Métriques d'évaluation
  - Optimisation des paramètres
  - Améliorations apportées

- **Documentation** (2 points)
  - Clarté du rapport
  - Justification des choix
  - Présentation des résultats

- **Présentation** (1 point)
  - Clarté de l'exposé
  - Qualité de la démonstration
  - Réponses aux questions

## Ressources

- [Documentation Spark MLlib](https://spark.apache.org/docs/latest/ml-guide.html)
- [Documentation ALS](https://spark.apache.org/docs/latest/ml-collaborative-filtering.html)
- [Métriques d'évaluation](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval))

## Conseils

1. Commencez par une analyse approfondie des données
2. Testez les paramètres de manière systématique
3. Documentez vos expérimentations
4. Utilisez la visualisation pour mieux comprendre les résultats
5. N'oubliez pas de gérer les cas particuliers (cold start, sparsity) 