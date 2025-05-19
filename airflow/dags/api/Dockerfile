FROM python:3.9-buster

WORKDIR /app

# Installation de Java 11
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Configuration de JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Copie des dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip config set global.timeout 1000 && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -r requirements.txt

# Copie du code source
COPY . .

# Exposition des ports
EXPOSE 5000 8000

# Commande de démarrage
CMD ["python", "recommendation_api.py"] 