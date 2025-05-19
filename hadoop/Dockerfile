FROM openjdk:11-jdk
# Installation des dépendances
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    net-tools \
    procps \
    openssh-server \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*
# Configuration de SSH
RUN rm -rf /etc/ssh/ssh_host_* \
    && ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N "" \
    && ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N "" \
    && ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N "" \
    && mkdir -p /root/.ssh \
    && ssh-keygen -t rsa -f /root/.ssh/id_rsa -N "" \
    && cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys \
    && chmod 600 /root/.ssh/authorized_keys
# Configuration de Java
ENV JAVA_HOME=/usr/local/openjdk-11
ENV PATH=$PATH:$JAVA_HOME/bin
# Téléchargement et installation de Hadoop
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    && tar -xzf hadoop-${HADOOP_VERSION}.tar.gz \
    && mv hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
    && rm hadoop-${HADOOP_VERSION}.tar.gz
# Copie des fichiers de configuration
COPY conf/ ${HADOOP_HOME}/etc/hadoop/
COPY conf/hadoop-env.sh ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh
# Copie du script dinitialisation
COPY scripts/init-hadoop.sh ${HADOOP_HOME}/init-hadoop.sh
RUN chmod +x ${HADOOP_HOME}/init-hadoop.sh
# Création des répertoires nécessaires
RUN mkdir -p /hadoop/dfs/name /hadoop/dfs/data
# Variables denvironnement
ENV HDFS_NAMENODE_USER=root
ENV HDFS_DATANODE_USER=root
ENV HDFS_SECONDARYNAMENODE_USER=root
ENV YARN_RESOURCEMANAGER_USER=root
ENV YARN_NODEMANAGER_USER=root
WORKDIR ${HADOOP_HOME}
# Point dentrée pour exécuter le script dinitialisation
ENTRYPOINT ["/opt/hadoop/init-hadoop.sh"]
# Copie de linstallation Hadoop dans le répertoire local
RUN mkdir -p /hadoop_install && cp -r ${HADOOP_HOME}/* /hadoop_install/
