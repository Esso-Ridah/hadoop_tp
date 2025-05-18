FROM apache/hive:3.1.3

USER root

# Installer les dépendances nécessaires
RUN apt-get update && \
    apt-get install -y netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copier les scripts d'initialisation
COPY wait-for-it.sh /wait-for-it.sh
COPY init-hive-server.sh /init-hive-server.sh

# Rendre les scripts exécutables
RUN chmod +x /wait-for-it.sh /init-hive-server.sh

# Exposer les ports du serveur Hive
EXPOSE 10000 10002

# Définir le point d'entrée
ENTRYPOINT ["/init-hive-server.sh"] 