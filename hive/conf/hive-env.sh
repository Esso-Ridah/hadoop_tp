# Hive environment variables
export HADOOP_HOME=/opt/hadoop
export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
export HADOOP_COMMON_HOME=/opt/hadoop
export HADOOP_HDFS_HOME=/opt/hadoop
export HADOOP_MAPRED_HOME=/opt/hadoop
export HADOOP_YARN_HOME=/opt/hadoop

# Add Hadoop binaries to PATH
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Hive specific variables
export HIVE_HOME=/opt/hive
export PATH=$PATH:$HIVE_HOME/bin

# HDFS user variables
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root

# YARN user variables
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root 