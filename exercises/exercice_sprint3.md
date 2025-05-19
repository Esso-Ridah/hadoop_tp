# Exercice : Sprint 3 - Contraintes Business

## Contexte
Dans ce sprint, vous allez adapter le système de recommandation pour prendre en compte des contraintes business importantes :
1. Filtrer les recommandations selon l'âge des films
2. Prioriser les films récents
3. Calculer les métriques de performance business

## Objectifs
1. Modifier le pipeline de recommandation pour intégrer l'âge des films
2. Implémenter un système de priorisation des films récents
3. Ajouter des métriques de performance business

## Exercice

### Partie 1 : Intégration de l'âge des films
La fonction `prepare_data` a déjà été modifiée pour extraire l'année de sortie des films. Vous devez maintenant :
1. Modifier la fonction `train_als_model` pour prendre en compte l'âge des films
2. Ajuster les recommandations en fonction de l'âge des films

```python
def train_als_model(**context):
    """
    Entraîne le modèle ALS en prenant en compte l'âge des films
    - Charge les données préparées
    - Configure et entraîne le modèle
    - Ajuste les recommandations selon l'âge des films
    - Évalue les performances
    - Sauvegarde le modèle
    """
    # TODO: Implémenter la logique
    pass
```

### Partie 2 : Priorisation des films récents
Créez une fonction pour ajuster les scores de recommandation en fonction de l'âge des films :

```python
def adjust_recommendations_by_age(recommendations_df, movies_df):
    """
    Ajuste les scores de recommandation en fonction de l'âge des films
    - Priorise les films récents
    - Applique un facteur de décroissance pour les films plus anciens
    - Retourne les recommandations ajustées
    """
    # TODO: Implémenter la logique
    pass
```

### Partie 3 : Métriques de performance
Implémentez des métriques pour évaluer la performance business :

```python
def calculate_business_metrics(recommendations_df, movies_df):
    """
    Calcule les métriques de performance business
    - Distribution des années de sortie
    - Taux de films récents recommandés
    - ROI potentiel basé sur l'âge des films
    """
    # TODO: Implémenter la logique
    pass
```

## Indices
1. Pour la priorisation des films récents :
   - Utilisez une fonction de décroissance exponentielle
   - Définissez une année de référence (par exemple, l'année actuelle)
   - Ajustez les scores en fonction de la différence d'années

2. Pour les métriques business :
   - Calculez la distribution des années de sortie
   - Définissez un seuil pour les "films récents" (par exemple, < 5 ans)
   - Estimez le ROI en fonction de l'âge des films

## Critères d'évaluation
1. **Qualité de l'implémentation** (40%)
   - Code propre et bien documenté
   - Gestion appropriée des erreurs
   - Tests unitaires

2. **Performance des recommandations** (30%)
   - Équilibre entre pertinence et récence
   - Distribution appropriée des années
   - Métriques de performance business

3. **Innovation** (30%)
   - Approche créative pour la priorisation
   - Métriques business pertinentes
   - Optimisations proposées

## Livrables attendus
1. Code source modifié
2. Documentation des choix d'implémentation
3. Résultats des métriques de performance
4. Tests unitaires

## Bonus
- Implémentez un système de pondération dynamique
- Ajoutez des visualisations des métriques
- Proposez des optimisations supplémentaires 