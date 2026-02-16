#!/bin/bash
set -e

# Wait until LocalStack is healthy and SQS is running
until curl -s http://localhost:4566/health | grep '"sqs".*"running"' >/dev/null 2>&1; do
  echo "Waiting for LocalStack SQS..."
  sleep 1
done

# Create the SQS queue(s)
awslocal sqs create-queue --queue-name FILA-TEST || true

echo "Queues created."
