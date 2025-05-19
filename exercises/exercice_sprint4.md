# Exercice : Sprint 4 - API et Monitoring

## Contexte
Dans ce sprint, vous allez créer une API REST pour exposer les recommandations et mettre en place un système de monitoring. Cela permettra :
1. D'intégrer le système de recommandation dans d'autres applications
2. De suivre les performances du système
3. De détecter et résoudre rapidement les problèmes

## Objectifs
1. Créer une API REST pour les recommandations
2. Implémenter un système de monitoring
3. Mettre en place des métriques de performance

## Exercice

### Partie 1 : API REST
Créez une API REST avec Flask pour exposer les recommandations :

```python
from flask import Flask, jsonify, request
from pyspark.sql import SparkSession

app = Flask(__name__)

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    Endpoint pour obtenir les recommandations d'un utilisateur
    - Récupère les recommandations depuis HDFS
    - Filtre pour l'utilisateur spécifié
    - Retourne les recommandations au format JSON
    """
    # TODO: Implémenter la logique
    pass

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Endpoint pour obtenir les métriques du système
    - Nombre de recommandations générées
    - Temps de réponse moyen
    - Taux d'erreur
    """
    # TODO: Implémenter la logique
    pass
```

### Partie 2 : Monitoring
Implémentez un système de monitoring avec Prometheus :

```python
from prometheus_client import Counter, Histogram, start_http_server

# Métriques Prometheus
recommendation_counter = Counter('recommendations_total', 'Nombre total de recommandations générées')
response_time = Histogram('response_time_seconds', 'Temps de réponse des requêtes')
error_counter = Counter('errors_total', 'Nombre total d\'erreurs')

def monitor_recommendations():
    """
    Configure et démarre le serveur de métriques Prometheus
    - Expose les métriques sur un port spécifique
    - Configure les alertes si nécessaire
    """
    # TODO: Implémenter la logique
    pass
```

### Partie 3 : Cache et Performance
Optimisez les performances de l'API :

```python
from functools import lru_cache
import redis

def setup_cache():
    """
    Configure le système de cache
    - Utilise Redis pour le cache distribué
    - Configure la durée de vie des recommandations
    - Gère l'invalidation du cache
    """
    # TODO: Implémenter la logique
    pass
```

## Indices
1. Pour l'API REST :
   - Utilisez Flask pour créer l'API
   - Implémentez la pagination pour les recommandations
   - Ajoutez des paramètres de filtrage (nombre de recommandations, etc.)

2. Pour le monitoring :
   - Utilisez Prometheus pour les métriques
   - Configurez des alertes pour les seuils critiques
   - Visualisez les métriques avec Grafana

3. Pour le cache :
   - Utilisez Redis pour le cache distribué
   - Implémentez une stratégie de cache adaptative
   - Gérez l'invalidation du cache lors des mises à jour

## Critères d'évaluation
1. **Qualité de l'API** (40%)
   - Documentation claire
   - Gestion des erreurs
   - Tests d'intégration
   - Performance et scalabilité

2. **Monitoring** (30%)
   - Métriques pertinentes
   - Alertes configurables
   - Visualisation des données

3. **Cache et Performance** (30%)
   - Stratégie de cache efficace
   - Temps de réponse optimisé
   - Gestion de la charge

## Livrables attendus
1. Code source de l'API
2. Configuration du monitoring
3. Tests d'intégration
4. Documentation API
5. Dashboard Grafana

## Bonus
- Implémentez l'authentification API
- Ajoutez des endpoints pour les statistiques avancées
- Créez des visualisations personnalisées
- Mettez en place un système de A/B testing 