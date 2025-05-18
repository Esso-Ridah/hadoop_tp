FROM openjdk:11-jdk

# Install required packages
RUN apt-get update && apt-get install -y \
    wget \
    procps \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Download and install Hive
RUN wget https://archive.apache.org/dist/hive/hive-3.1.3/apache-hive-3.1.3-bin.tar.gz \
    && tar -xzf apache-hive-3.1.3-bin.tar.gz \
    && mv apache-hive-3.1.3-bin /opt/hive \
    && rm apache-hive-3.1.3-bin.tar.gz

# Download and install Hadoop
RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz \
    && tar -xzf hadoop-3.3.6.tar.gz \
    && mv hadoop-3.3.6 /opt/hadoop \
    && rm hadoop-3.3.6.tar.gz

# Set environment variables
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_PREFIX=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV HIVE_HOME=/opt/hive
ENV PATH=$PATH:$HIVE_HOME/bin
ENV JAVA_HOME=/usr/local/openjdk-11

# Copy configuration files
COPY conf/hive-site.xml /opt/hive/conf/
COPY conf/hive-env.sh /opt/hive/conf/
COPY scripts/init-hive.sh /opt/hive/init-hive.sh

# Make init script executable
RUN chmod +x /opt/hive/init-hive.sh

# Create Hive directories
RUN mkdir -p /tmp/hive

WORKDIR /opt/hive

CMD ["/opt/hive/init-hive.sh"] 