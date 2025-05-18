FROM apache/airflow:2.8.1

USER root

# Installer Java, Docker et Spark
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    wget && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r docker || true && \
    usermod -aG docker airflow && \
    wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz && \
    tar xzf spark-3.5.0-bin-hadoop3.tgz -C /opt && \
    rm spark-3.5.0-bin-hadoop3.tgz && \
    ln -s /opt/spark-3.5.0-bin-hadoop3 /opt/spark

USER airflow
RUN pip install --user apache-airflow-providers-apache-spark
ENV PATH="/home/airflow/.local/bin:/opt/spark/bin:$PATH"
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV SPARK_HOME="/opt/spark"

USER root

# Installer le package Spark
RUN /usr/local/bin/pip install --no-cache-dir apache-airflow-providers-apache-spark

USER airflow 