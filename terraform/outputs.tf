output "s3_bucket_id" {
  description = "ID do Bucket criado"
  value       = aws_s3_bucket.videos_bucket.id
}

output "sqs_queue_url" {
  description = "URL da Fila SQS criada"
  value       = aws_sqs_queue.video_queue.url
}
