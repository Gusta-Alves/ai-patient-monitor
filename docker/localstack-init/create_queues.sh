#!/bin/bash
# IMPORTANTE: Salve este arquivo com quebra de linha LF (Unix) no VS Code (canto inferior direito).
echo "### INICIANDO SCRIPT DE CONFIGURACAO (create_queues.sh) ###"
set -e

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Wait until LocalStack is healthy and SQS is running
# until curl -s http://localhost:4566/health | grep '"sqs".*"running"' >/dev/null 2>&1; do
#   echo "Waiting for LocalStack SQS..."
#   sleep 1
# done

# Create the SQS queue(s)
echo "Creating SQS Queue..."
aws --endpoint-url=http://localhost:4566 --region us-east-1 sqs create-queue --queue-name FILA-MONITORAMENTO-IDOSOS

echo "Creating S3 Bucket..."
aws --endpoint-url=http://localhost:4566 --region us-east-1 s3 mb s3://bucket-videos-monitoramento

echo "Queues created."

echo "Checking if video file exists in container..."
ls -l /tmp/Video_Deitado_Gritando_Socorro.mp4

echo "Uploading video to S3..."
aws --endpoint-url=http://localhost:4566 --region us-east-1 s3 cp /tmp/Video_Deitado_Gritando_Socorro.mp4 s3://bucket-videos-monitoramento/Video_Deitado_Gritando_Socorro.mp4

echo "Initialization script finished."
