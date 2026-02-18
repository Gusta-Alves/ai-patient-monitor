import boto3
import json
import os
import datetime


class SQSClient:
    def __init__(self, queue_url, useLocalStack, region_name='us-east-1'):
        """
        Inicializa o cliente SQS. 
        Certifique-se de ter as credenciais configuradas no ambiente ou no ~/.aws/credentials
        """
        self.region_name = region_name
        self.useLocalStack = useLocalStack
        self._get_client()
        
        # Lógica inteligente: Resolve URL ou cria fila no LocalStack
        if not queue_url.startswith("http"):
            try:
                self.queue_url = self.sqs.get_queue_url(QueueName=queue_url)['QueueUrl']
            except Exception:
                # Se falhar e for LocalStack, cria a fila automaticamente
                if str(self.useLocalStack).lower() == "true" or self.useLocalStack is True:
                    print(f"⚠️ [LocalStack] Fila '{queue_url}' não encontrada. Criando automaticamente...")
                    self.queue_url = self.sqs.create_queue(QueueName=queue_url)['QueueUrl']
                else:
                    # Em produção (AWS), deve falhar se a fila não existir (Terraform deve criar)
                    raise Exception(f"Fila '{queue_url}' não encontrada na AWS.")
        else:
            self.queue_url = queue_url

    def _get_client(self):
        """
        Retorna o cliente SQS para uso direto, se necessário.
        """
        if str(self.useLocalStack).lower() == "true" or self.useLocalStack is True:
            os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
            os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
            os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
            self.sqs = boto3.client('sqs', endpoint_url="http://localhost:4566", region_name=self.region_name)
        else:
            self.sqs = boto3.client('sqs', region_name=self.region_name)
        return self.sqs

    def send_alert(self, alert_type, message, metadata=None):
        """
        Envia uma mensagem de alerta para a fila SQS.
        """
        payload = {
            "alert_type": alert_type,
            "message": message,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {}
        }

        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(payload),
                MessageAttributes={
                    'AlertType': {
                        'StringValue': alert_type,
                        'DataType': 'String'
                    }
                }
            )
            print(
                f"Alerta enviado com sucesso! MessageId: {response.get('MessageId')}")
            return response
        except Exception as e:
            print(f"Erro ao enviar mensagem para o SQS: {e}")
            return None
