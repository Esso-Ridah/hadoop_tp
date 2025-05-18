#!/bin/bash
set -e

# Wait for namenode to be ready
until nc -z namenode 9000; do
  echo "Waiting for namenode to be ready..."
  sleep 1
done

# Wait for metastore to be ready
/wait-for-it.sh hive-metastore:9083 -t 60

# Start Hive server
echo "Starting Hive server..."
exec hive --service hiveserver2 