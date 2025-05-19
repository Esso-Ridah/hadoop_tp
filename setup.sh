#!/bin/bash

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    print_message "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier les permissions Docker
    if ! docker info &> /dev/null; then
        print_error "Vous n'avez pas les permissions pour exécuter Docker. Ajoutez votre utilisateur au groupe docker."
        exit 1
    fi
}

# Création des répertoires nécessaires
create_directories() {
    print_message "Création des répertoires nécessaires..."
    
    # Créer les répertoires pour les données persistantes
    mkdir -p data/namenode
    mkdir -p data/datanode1
    mkdir -p data/datanode2
    mkdir -p data/datanode3
    mkdir -p data/postgres
    mkdir -p data/spark
    
    # Créer les répertoires pour Airflow
    mkdir -p airflow/dags
    mkdir -p airflow/logs
    mkdir -p airflow/plugins
    mkdir -p airflow/dags/api
    mkdir -p airflow/dags/monitoring
}

# Configuration des permissions
setup_permissions() {
    print_message "Configuration des permissions..."
    
    # Donner les permissions nécessaires aux répertoires
    chmod -R 777 data/
    chmod -R 777 airflow/
    
    # Définir l'UID Airflow
    export AIRFLOW_UID=$(id -u)
}

# Construction et démarrage des conteneurs
start_containers() {
    print_message "Construction et démarrage des conteneurs..."
    
    # Arrêter les conteneurs existants et supprimer les volumes
    docker-compose down -v
    
    # Supprimer les données existantes
    sudo rm -rf data/postgres/*
    
    # Démarrer d'abord PostgreSQL
    docker-compose up -d postgres
    
    # Attendre que PostgreSQL soit prêt
    print_message "Attente du démarrage de PostgreSQL..."
    sleep 30
    
    # Démarrer les autres services
    docker-compose up -d
}

# Initialisation d'Airflow
setup_airflow() {
    print_message "Initialisation d'Airflow..."
    
    # Attendre que les services soient prêts
    sleep 30
    
    # Initialiser la base de données
    docker exec -it airflow-webserver airflow db migrate
    
    # Créer l'utilisateur admin
    docker exec -it airflow-webserver airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin
}

# Test des connexions
test_connections() {
    print_message "Test des connexions..."
    
    # Test de la connexion à HDFS
    print_message "Test de la connexion à HDFS..."
    docker exec -it namenode hdfs dfs -ls /
    
    # Test de la connexion à YARN
    print_message "Test de la connexion à YARN..."
    docker exec -it resourcemanager yarn node -list
    
    # Test de la connexion à Spark
    print_message "Test de la connexion à Spark..."
    docker exec -it spark-master spark-sql -e "SHOW DATABASES;"
    
    # Vérification des datanodes HDFS
    print_message "Vérification des datanodes HDFS..."
    docker exec -it namenode hdfs dfsadmin -report | grep "Live datanodes"
    
    # Création du répertoire Airflow dans HDFS
    print_message "Création du répertoire Airflow dans HDFS..."
    docker exec -it namenode hdfs dfs -mkdir -p /user/airflow
    
    # Test d'écriture/lecture dans HDFS
    print_message "Test d'écriture/lecture dans HDFS..."
    docker exec -it namenode bash -c 'echo "Test HDFS write/read" > test.txt && hdfs dfs -put test.txt /user/airflow/test.txt && hdfs dfs -cat /user/airflow/test.txt && hdfs dfs -ls /user/airflow/'
}

# Test des DAGs MovieLens
test_movielens_dags() {
    print_message "Test des DAGs MovieLens..."
    
    # Attendre que Airflow soit complètement démarré
    sleep 30
    
    # Copier les DAGs MovieLens
    print_message "Copie des DAGs MovieLens..."
    cp movielens_ingestion.py airflow/dags/
    cp movie_recommendation.py airflow/dags/
    
    # Attendre que les DAGs soient détectés
    print_message "Attente de la détection des DAGs..."
    sleep 30
    
    # Déclencher le DAG d'ingestion
    print_message "Déclenchement du DAG d'ingestion..."
    docker exec -it airflow-webserver airflow dags trigger movielens_ingestion
    
    # Attendre que l'ingestion soit terminée
    print_message "Attente de la fin de l'ingestion..."
    sleep 60
    
    # Déclencher le DAG de recommandation
    print_message "Déclenchement du DAG de recommandation..."
    docker exec -it airflow-webserver airflow dags trigger movie_recommendation
    
    print_message "Les DAGs MovieLens ont été déclenchés. Vérifiez l'interface Airflow pour suivre leur exécution."
}

# Déploiement et test de la visualisation Flask
setup_viewer() {
    print_message "Déploiement de l'interface Flask de visualisation..."
    
    # Nettoyer les anciens conteneurs
    docker stop movie-recommendation-viewer 2>/dev/null || true
    docker rm movie-recommendation-viewer 2>/dev/null || true

    # Construire l'image Docker
    if ! docker build -t movie-recommendation-viewer -f Dockerfile.viewer .; then
        print_error "Échec de la construction de l'image Docker"
        exit 1
    fi

    # Démarrer le conteneur
    if ! docker run -d \
        --name movie-recommendation-viewer \
        --network hadoop_tp_hadoop_network \
        -p 5000:5000 \
        movie-recommendation-viewer; then
        print_error "Échec du démarrage du conteneur Flask viewer"
        exit 1
    fi

    # Vérifier que le conteneur est en cours d'exécution
    if ! docker ps | grep -q movie-recommendation-viewer; then
        print_error "Le conteneur Flask viewer n'est pas en cours d'exécution"
        docker logs movie-recommendation-viewer
        exit 1
    fi

    # Test de connectivité réseau depuis le conteneur Flask
    print_message "Test de connectivité réseau depuis le conteneur Flask (ping namenode)..."
    if ! docker exec -it movie-recommendation-viewer ping -c 2 namenode; then
        print_warning "Le conteneur Flask viewer ne peut pas joindre le namenode. Vérifiez la configuration réseau."
    else
        print_message "Connectivité réseau OK."
    fi

    print_message "L'application Flask de visualisation est accessible à l'adresse : http://localhost:5000"
    print_message "Pour voir les logs : docker logs movie-recommendation-viewer"
    print_message "Pour arrêter l'application : docker stop movie-recommendation-viewer"
}

# Création du fichier .env pour Airflow
echo "AIRFLOW_UID=$(id -u)" > .env

# Création du fichier hadoop.env
cat > hadoop.env << EOL
CORE_CONF_fs_defaultFS=hdfs://namenode:9000
CORE_CONF_hadoop_http_staticuser_user=root
CORE_CONF_hadoop_proxyuser_hue_hosts=*
CORE_CONF_hadoop_proxyuser_hue_groups=*
CORE_CONF_io_compression_codecs=org.apache.hadoop.io.compress.SnappyCodec

HDFS_CONF_dfs_webhdfs_enabled=true
HDFS_CONF_dfs_permissions_enabled=false
HDFS_CONF_dfs_namenode_datanode_registration_ip___hostname___check=false

MAPRED_CONF_mapreduce_framework_name=yarn
MAPRED_CONF_mapreduce_map_java_opts=-Xmx4096m
MAPRED_CONF_mapreduce_reduce_java_opts=-Xmx4096m
MAPRED_CONF_mapreduce_map_memory_mb=4096
MAPRED_CONF_mapreduce_reduce_memory_mb=4096
MAPRED_CONF_yarn_app_mapreduce_am_resource_mb=4096
MAPRED_CONF_yarn_app_mapreduce_am_command_opts=-Xmx4096m
EOL

# Installation des dépendances Python pour l'API
pip install flask==2.0.1 pyspark==3.1.1 prometheus-client==0.11.0 python-dotenv==0.19.0 requests==2.26.0 gunicorn==20.1.0

# Configuration de Prometheus
cat > airflow/dags/monitoring/prometheus.yml << EOL
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'recommendation_api'
    static_configs:
      - targets: ['recommendation-api:8000']
    metrics_path: '/metrics'

  - job_name: 'hadoop'
    static_configs:
      - targets: ['namenode:9870']
    metrics_path: '/jmx'

  - job_name: 'spark'
    static_configs:
      - targets: ['spark-master:8080']
    metrics_path: '/metrics'
EOL

# Configuration du dashboard Grafana
cat > airflow/dags/monitoring/grafana_dashboard.json << EOL
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "expr": "rate(recommendations_total[5m])",
          "refId": "A"
        }
      ],
      "title": "Taux de recommandations",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "s"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 2,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "expr": "rate(response_time_seconds_sum[5m]) / rate(response_time_seconds_count[5m])",
          "refId": "A"
        }
      ],
      "title": "Temps de réponse moyen",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "percentunit"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 8
      },
      "id": 3,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "expr": "rate(errors_total[5m]) / (rate(recommendations_total[5m]) + rate(errors_total[5m]))",
          "refId": "A"
        }
      ],
      "title": "Taux d'erreur",
      "type": "timeseries"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Dashboard Recommandations",
  "uid": "recommendations",
  "version": 1,
  "weekStart": ""
}
EOL

# Création du Dockerfile pour l'API
cat > airflow/dags/api/Dockerfile << EOL
FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \\
    openjdk-11-jdk \\
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Exposition des ports
EXPOSE 5000 8000

# Démarrage de l'API
CMD ["python", "recommendation_api.py"]
EOL

# Création du fichier requirements.txt pour l'API
cat > airflow/dags/api/requirements.txt << EOL
flask==2.0.1
pyspark==3.1.1
prometheus-client==0.11.0
python-dotenv==0.19.0
requests==2.26.0
gunicorn==20.1.0
EOL

# Création du fichier recommendation_api.py
cat > airflow/dags/api/recommendation_api.py << EOL
from flask import Flask, jsonify, request
from pyspark.sql import SparkSession
from prometheus_client import Counter, Histogram, start_http_server
import time
import logging
from functools import wraps

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Métriques Prometheus
recommendation_counter = Counter('recommendations_total', 'Nombre total de recommandations générées')
response_time = Histogram('response_time_seconds', 'Temps de réponse des requêtes')
error_counter = Counter('errors_total', 'Nombre total d\'erreurs')

# Décorateur pour mesurer le temps de réponse
def track_time(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            response_time.observe(time.time() - start_time)
            return result
        except Exception as e:
            error_counter.inc()
            logger.error(f"Erreur: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return decorated_function

def get_spark_session():
    """Crée ou récupère une session Spark"""
    return SparkSession.builder \\
        .appName("RecommendationAPI") \\
        .config("spark.driver.memory", "2g") \\
        .config("spark.executor.memory", "2g") \\
        .getOrCreate()

@app.route('/recommendations/<int:user_id>', methods=['GET'])
@track_time
def get_recommendations(user_id):
    """Endpoint pour obtenir les recommandations d'un utilisateur"""
    try:
        spark = get_spark_session()
        
        # Lecture des recommandations depuis HDFS
        recommendations_df = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/recommendations")
        
        # Filtrage pour l'utilisateur spécifié
        user_recommendations = recommendations_df.filter(f"userId = {user_id}")
        
        # Conversion en liste de dictionnaires
        recommendations = user_recommendations.collect()
        
        # Incrémentation du compteur de recommandations
        recommendation_counter.inc(len(recommendations))
        
        return jsonify({
            "user_id": user_id,
            "recommendations": [{
                "movieId": row.movieId,
                "title": row.title,
                "score": row.score
            } for row in recommendations]
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des recommandations: {str(e)}")
        error_counter.inc()
        return jsonify({"error": str(e)}), 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Endpoint pour obtenir les métriques du système"""
    try:
        spark = get_spark_session()
        
        # Lecture des statistiques depuis HDFS
        stats_df = spark.read.parquet("hdfs://namenode:9000/user/airflow/movielens/stats")
        
        # Conversion en dictionnaire
        stats = stats_df.collect()[0].asDict()
        
        return jsonify({
            "total_recommendations": recommendation_counter._value.get(),
            "average_response_time": response_time._sum.get() / response_time._count.get() if response_time._count.get() > 0 else 0,
            "error_rate": error_counter._value.get() / (recommendation_counter._value.get() + error_counter._value.get()) if (recommendation_counter._value.get() + error_counter._value.get()) > 0 else 0,
            "system_stats": stats
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint pour vérifier l'état du service"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Démarrage du serveur de métriques Prometheus
    start_http_server(8000)
    # Démarrage de l'API Flask
    app.run(host='0.0.0.0', port=5000)
EOL

# Test de l'API et du monitoring
test_api_and_monitoring() {
    print_message "Test de l'API et du monitoring..."
    
    # Attendre que les services soient prêts
    sleep 30
    
    # Test de l'API
    print_message "Test de l'API..."
    
    # Test de l'endpoint health
    print_message "Test de l'endpoint /health..."
    if ! curl -s http://localhost:5000/health | grep -q "healthy"; then
        print_error "L'endpoint /health ne répond pas correctement"
        return 1
    fi
    
    # Test de l'endpoint metrics
    print_message "Test de l'endpoint /metrics..."
    if ! curl -s http://localhost:5000/metrics | grep -q "recommendations_total"; then
        print_error "L'endpoint /metrics ne répond pas correctement"
        return 1
    fi
    
    # Test de l'endpoint recommendations
    print_message "Test de l'endpoint /recommendations..."
    if ! curl -s http://localhost:5000/recommendations/1 | grep -q "user_id"; then
        print_error "L'endpoint /recommendations ne répond pas correctement"
        return 1
    fi
    
    # Test de Prometheus
    print_message "Test de Prometheus..."
    if ! curl -s http://localhost:9090/-/healthy | grep -q "OK"; then
        print_error "Prometheus n'est pas en bonne santé"
        return 1
    fi
    
    # Vérifier que les métriques sont collectées
    if ! curl -s http://localhost:9090/api/v1/query?query=recommendations_total | grep -q "result"; then
        print_error "Prometheus ne collecte pas les métriques"
        return 1
    fi
    
    # Test de Grafana
    print_message "Test de Grafana..."
    if ! curl -s http://localhost:3000/api/health | grep -q "ok"; then
        print_error "Grafana n'est pas en bonne santé"
        return 1
    fi
    
    # Vérifier que le dashboard est chargé
    if ! curl -s -u admin:admin http://localhost:3000/api/dashboards/uid/recommendations | grep -q "dashboard"; then
        print_error "Le dashboard Grafana n'est pas correctement configuré"
        return 1
    fi
    
    print_message "Tests de l'API et du monitoring réussis !"
    return 0
}

# Rendre le script exécutable
chmod +x setup.sh

echo "Configuration terminée !"

# Fonction principale
main() {
    check_prerequisites
    create_directories
    setup_permissions
    start_containers
    setup_airflow
    test_connections
    test_movielens_dags
    setup_viewer
    test_api_and_monitoring
    print_message "Installation terminée avec succès !"
    print_message "Interfaces web disponibles :"
    print_message "- HDFS NameNode : http://localhost:9870"
    print_message "- YARN ResourceManager : http://localhost:8088"
    print_message "- Spark Master : http://localhost:8080"
    print_message "- Airflow : http://localhost:8081 (utilisateur: admin, mot de passe: admin)"
    print_message "- Visualisation recommandations : http://localhost:5000"
    print_message "- Prometheus : http://localhost:9090"
    print_message "- Grafana : http://localhost:3000 (utilisateur: admin, mot de passe: admin)"
    print_message "Les DAGs MovieLens ont été déclenchés. Vérifiez l'interface Airflow pour suivre leur exécution."
}

# Exécution du script
main 