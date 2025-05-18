FROM apache/hive:3.1.3

USER root

# Installer les dépendances nécessaires
RUN apt-get update && \
    apt-get install -y netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copier les scripts d'initialisation
COPY wait-for-it.sh /wait-for-it.sh
COPY entrypoint.sh /entrypoint.sh

# Rendre les scripts exécutables
RUN chmod +x /wait-for-it.sh /entrypoint.sh

# Exposer le port du metastore
EXPOSE 9083

# Définir le point d'entrée
ENTRYPOINT ["/entrypoint.sh"]