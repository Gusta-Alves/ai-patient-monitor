# --- S3 Bucket ---
resource "aws_s3_bucket" "videos_bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = "Patient Monitor Videos"
    Environment = "Dev"
  }
}

# Bloqueio de acesso público (Segurança)
resource "aws_s3_bucket_public_access_block" "videos_bucket_block" {
  bucket = aws_s3_bucket.videos_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- SQS Queue ---
resource "aws_sqs_queue" "video_queue" {
  name                      = var.queue_name
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 86400 # 1 dia
  receive_wait_time_seconds = 10    # Long polling
}
