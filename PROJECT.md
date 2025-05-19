# Projet CineMatch : Système de Recommandation de Films

## Contexte du Projet

### Client
CineMatch est une startup française de VOD (Vidéo à la Demande) qui souhaite améliorer son système de recommandation pour augmenter le taux de rétention de ses abonnés.

### Enjeux
- Augmenter le temps de visionnage des utilisateurs
- Améliorer la pertinence des recommandations
- Optimiser les coûts de droits d'auteur
- Maintenir une expérience utilisateur de qualité

### Objectifs Business
- Augmentation de 2% du temps de visionnage = 120k€/an
- Réduction des coûts de droits d'auteur
- Amélioration de la satisfaction utilisateur

## Environnement Technique

### Infrastructure
- Cluster Hadoop : 3 nœuds
- Apache Spark pour le traitement
- Apache Airflow pour l'orchestration
- API REST pour l'intégration

### Données
- Dataset MovieLens (25M)
- Catalogue des droits acquis (XML)
- Historique des visionnages

## Phases du Projet

### Phase 1 : Base du Projet ✅
**État** : Complété

#### Composants fournis
- Environnement Hadoop/Spark/Airflow
- Pipeline d'ingestion MovieLens
- Scripts de vérification des données

#### Objectifs atteints
- Installation et configuration de l'environnement
- Ingestion des données MovieLens
- Vérification de l'intégrité des données

### Phase 2 : Développement du Système de Recommandation (Optionnelle)

#### Recommandation Basique
**État** : Complétée et fournie

##### Base fournie
- Structure du DAG Airflow
- Schéma de données
- Tests unitaires de base

##### Objectifs
1. Implémenter l'algorithme ALS avec Spark MLlib
2. Créer le pipeline de traitement
3. Stocker les recommandations

##### Critères d'évaluation
- Qualité de l'implémentation ALS
- Performance du modèle
- Documentation du code
- Tests unitaires

##### Exercice 1
```python
def train_als_model(ratings_df):
    """
    Entraîner un modèle ALS avec les paramètres optimaux
    - Trouver les meilleurs paramètres (rank, regParam, etc.)
    - Gérer la validation croisée
    - Sauvegarder le modèle
    """
    pass
```

#### Sprint 2 : Optimisation des Performances
**État** : Optionnel

##### Base fournie
- Code du Sprint 1
- Métriques de performance de base
- Outils de monitoring

##### Objectifs
1. Optimiser les partitions Spark
2. Implémenter le caching intelligent
3. Réduire le temps d'exécution à <1h

##### Critères d'évaluation
- Temps d'exécution
- Utilisation des ressources
- Qualité des optimisations
- Documentation des choix

##### Exercice
```python
def optimize_spark_job():
    """
    Optimiser les performances du job Spark
    - Analyser le plan d'exécution
    - Identifier les goulots d'étranglement
    - Proposer des optimisations
    """
    pass
```

#### Sprint 3 : Contraintes Business (Obligatoire)
**État** : À venir

##### Base fournie
- Code optimisé du Sprint 2
- Règles métier détaillées
- Métriques business

##### Objectifs
1. Filtrer les recommandations selon l'âge
2. Prioriser les films récents
3. Calculer les métriques de performance

##### Critères d'évaluation
- Respect des contraintes business
- Qualité des recommandations
- Calcul du ROI
- Documentation des choix

##### Exercice
```python
def apply_business_rules(recommendations_df):
    """
    Appliquer les règles métier aux recommandations
    - Filtrer le contenu >18 ans
    - Prioriser les films récents
    - Calculer le ROI potentiel
    """
    pass
```

#### Sprint 4 : API et Monitoring (Optionnelle)
**État** : À venir

##### Base fournie
- Code du Sprint 3
- Structure de l'API
- Framework de monitoring

##### Objectifs
1. Créer l'endpoint REST
2. Implémenter les métriques
3. Mettre en place le monitoring

##### Critères d'évaluation
- Qualité de l'API
- Performance du système
- Documentation API
- Tests d'intégration

##### Exercice
```python
def create_recommendation_api():
    """
    Créer l'API de recommandation
    - Implémenter l'endpoint REST
    - Gérer le cache
    - Mettre en place les métriques
    """
    pass
```

## Évaluation Globale

### Critères d'évaluation
1. **Qualité du Code** (30%)
   - Structure et organisation
   - Tests unitaires
   - Documentation
   - Gestion des erreurs

2. **Performance** (25%)
   - Temps d'exécution
   - Utilisation des ressources
   - Scalabilité
   - Optimisations

3. **Fonctionnalités** (25%)
   - Respect des exigences
   - Qualité des recommandations
   - Intégration des contraintes business
   - API et monitoring

4. **Documentation et Présentation** (20%)
   - Documentation technique
   - Présentation des résultats
   - Justification des choix
   - ROI et métriques business

### Livrables attendus
1. Code source commenté
2. Documentation technique
3. Présentation des résultats
4. Démonstration du système
5. Rapport de performance

## Ressources

### Documentation
- [Documentation Spark MLlib](https://spark.apache.org/docs/latest/ml-collaborative-filtering.html)
- [Documentation Airflow](https://airflow.apache.org/docs/)
- [Documentation MovieLens](https://grouplens.org/datasets/movielens/)

### Outils
- Spark UI pour le monitoring
- Airflow UI pour l'orchestration
- Git pour le versioning

### Organisation du Travail
- Travail en groupe
- Organisation libre des tâches
- Collaboration via Git
- Communication régulière avec l'équipe pédagogique

## Contact

Pour toute question concernant le projet, veuillez contacter l'équipe pédagogique. 