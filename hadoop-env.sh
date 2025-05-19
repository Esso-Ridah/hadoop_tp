export JAVA_HOME=/usr/local/openjdk-11

# JMX Configuration
export HDFS_NAMENODE_OPTS="$HDFS_NAMENODE_OPTS -javaagent:/opt/jmx_prometheus_javaagent.jar=9404:/opt/hadoop/etc/hadoop/jmx-config.yml"
export HDFS_DATANODE_OPTS="$HDFS_DATANODE_OPTS -javaagent:/opt/jmx_prometheus_javaagent.jar=9405:/opt/hadoop/etc/hadoop/jmx-config.yml"
export HDFS_SECONDARYNAMENODE_OPTS="$HDFS_SECONDARYNAMENODE_OPTS -javaagent:/opt/jmx_prometheus_javaagent.jar=9406:/opt/hadoop/etc/hadoop/jmx-config.yml" 