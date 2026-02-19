variable "aws_region" {
  description = "Região da AWS onde os recursos serão criados"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Nome único do bucket S3 para vídeos (deve ser globalmente único)"
  type        = string
  default     = "ai-patient-monitor-videos-input-v1"
}

variable "queue_name" {
  description = "Nome da fila SQS para processamento"
  type        = string
  default     = "FILA-MONITORAMENTO-IDOSOS"
}