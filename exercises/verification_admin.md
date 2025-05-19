# Exercice : Administration et Gestion d'un Système Hadoop

## Contexte
Dans cet exercice, vous allez mettre en place et gérer un cluster Hadoop pour le système de recommandation de films. Vous devrez :
1. Configurer et maintenir un cluster Hadoop
2. Gérer les ressources et la performance
3. Assurer la fiabilité et la disponibilité du système

## Objectifs
1. Comprendre l'architecture d'un cluster Hadoop
2. Maîtriser les commandes de gestion HDFS
3. Optimiser les performances du cluster
4. Gérer la sécurité et les permissions

## Exercice

### Partie 1 : Configuration du Cluster
1. **Architecture du Cluster**
   - Identifiez les composants nécessaires (NameNode, DataNodes, etc.)
   - Définissez la topologie réseau
   - Configurez les paramètres de base

2. **Configuration HDFS**
   - Définissez les paramètres de réplication
   - Configurez les quotas d'espace
   - Mettez en place les permissions

### Partie 2 : Gestion des Données
1. **Opérations HDFS**
   ```bash
   # TODO: Implémentez les commandes pour :
   - Lister les fichiers et répertoires
   - Vérifier l'espace disponible
   - Gérer les permissions
   - Surveiller l'état du cluster
   ```

2. **Maintenance**
   - Nettoyage des fichiers temporaires
   - Gestion des logs
   - Sauvegarde des métadonnées

### Partie 3 : Performance et Monitoring
1. **Optimisation**
   - Ajustement des paramètres de performance
   - Gestion de la mémoire
   - Optimisation des I/O

2. **Surveillance**
   - Monitoring des ressources
   - Détection des goulots d'étranglement
   - Alertes de performance

## Tâches Pratiques

### Tâche 1 : Configuration Initiale
1. Configurez un cluster Hadoop avec :
   - 1 NameNode
   - 3 DataNodes
   - Configuration de réplication à 3
   - Quotas d'espace par utilisateur

2. Vérifiez la configuration avec :
   ```bash
   hdfs dfsadmin -report
   hdfs dfsadmin -safemode get
   ```

### Tâche 2 : Gestion des Données
1. Créez la structure de répertoires pour le projet :
   ```
   /user/airflow/
   ├── movielens/
   │   ├── raw/
   │   ├── processed/
   │   └── recommendations/
   └── logs/
   ```

2. Configurez les permissions :
   ```bash
   hdfs dfs -chmod -R 755 /user/airflow
   hdfs dfs -chown -R airflow:airflow /user/airflow
   ```

### Tâche 3 : Monitoring et Maintenance
1. Mettez en place un script de maintenance quotidienne :
   - Nettoyage des fichiers temporaires
   - Vérification de l'espace disque
   - Sauvegarde des métadonnées

2. Créez un dashboard de monitoring avec :
   - État des DataNodes
   - Utilisation de l'espace
   - Performance des I/O

## Critères d'évaluation
1. **Configuration du Cluster** (30%)
   - Architecture correcte
   - Paramètres optimisés
   - Sécurité mise en place

2. **Gestion des Données** (30%)
   - Structure de répertoires appropriée
   - Permissions correctes
   - Maintenance régulière

3. **Performance et Monitoring** (40%)
   - Métriques pertinentes
   - Scripts de maintenance
   - Documentation claire

## Livrables attendus
1. Documentation de l'architecture
2. Scripts de configuration et maintenance
3. Dashboard de monitoring
4. Procédures de sauvegarde
5. Guide d'administration

## Bonus
- Automatisation complète du déploiement
- Système de backup et recovery
- Monitoring avancé avec alertes
- Optimisation des performances

## Ressources
- [Documentation HDFS](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html)
- [Guide d'administration Hadoop](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/AdminGuide.html)
- [Best Practices Hadoop](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/ClusterSetup.html) 