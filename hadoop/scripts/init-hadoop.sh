#!/bin/bash
source /opt/hadoop/etc/hadoop/hadoop-env.sh
export JAVA_HOME=/usr/local/openjdk-11
export PATH=$PATH:$JAVA_HOME/bin
if [ -z "$JAVA_HOME" ]; then
    echo "ERROR: JAVA_HOME is not set"
    exit 1
fi
if ! command -v java &> /dev/null; then
    echo "ERROR: Java is not accessible"
    exit 1
fi
service ssh start
set -e
format_namenode() {
    echo "Formatting namenode..."
    echo "Y" | hdfs namenode -format
}
start_hdfs() {
    echo "Starting HDFS services..."
    start-dfs.sh
}
start_yarn() {
    echo "Starting YARN services..."
    start-yarn.sh
}
check_status() {
    echo "Checking HDFS status..."
    hdfs dfsadmin -report
    echo "Checking YARN status..."
    yarn node -list
}
case "$(hostname)" in
    "namenode")
        format_namenode
        start_hdfs
        check_status
        ;;
    "resourcemanager")
        start_yarn
        check_status
        ;;
    "datanode"*)
        echo "Starting datanode services..."
        hdfs datanode
        ;;
esac
tail -f /dev/null
