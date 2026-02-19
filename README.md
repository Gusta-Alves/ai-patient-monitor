# 🏥 Sistema de Monitoramento Inteligente de Pacientes

Sistema completo de IA multimodal para detecção de quedas, análise de vídeo e transcrição automática, com integração em nuvem AWS via API REST segura.

**Funcionalidades principais:**
- 🎥 Detecção de quedas em tempo real com YOLOv8
- 🎙️ Transcrição de áudio automática (Google Speech Recognition)
- 🧠 Análise multimodal com IA (vídeo + áudio)
- ☁️ Integração AWS (S3, SQS, Cognito)
- 🔐 Autenticação segura via Cognito
- 🚀 API REST com FastAPI
- 🐳 Suporte a Docker e LocalStack

## 📋 Funcionalidades Detalhadas

### 1. Detecção de Quedas (`fall_detection.py`)
- **Detecção de pessoas** usando YOLOv8 pose estimation
- **Máquina de estados** para evitar falsos alarmes
- **Múltiplos critérios de análise**:
  - Aspect ratio do corpo (deitado vs em pé)
  - Posição vertical dos keypoints
  - Velocidade de descida
  - Análise da postura corporal
- **Regra de segurança**: Se houver mais de uma pessoa na cena, considera seguro (com assistência)

### 2. Transcrição de Vídeo (`transcribe_video.py`)
- Extração de áudio de arquivos de vídeo
- Transcrição automática usando Google Speech Recognition
- Suporte para múltiplos idiomas (configurado para pt-BR)

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd "fase 4 - pos/Aula 4"
```

2. Crie um ambiente virtual:
```bash
python -m venv .venv

# No macOS/Linux:
source .venv/bin/activate

# No Windows:
.venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Baixe o modelo YOLOv8:
O modelo `yolov8n-pose.pt` será baixado automaticamente na primeira execução, ou baixe manualmente de:
https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-pose.pt

## 🌍 Variáveis de Ambiente

### Configuração Básica (.env)

Crie um arquivo `.env` na raiz do projeto com as variáveis necessárias:

```bash
# ===== CONFIGURAÇÕES AWS =====
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# ===== CONFIGURAÇÕES SQS =====
QUEUE_URL=FILA-MONITORAMENTO-IDOSOS
# ou use a URL completa se preferir:
# QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789/FILA-MONITORAMENTO-IDOSOS

# ===== CONFIGURAÇÕES S3 =====
# Nome do bucket para armazenar vídeos
BUCKET_NAME=bucket-videos-monitoramento

# ===== AUTENTICAÇÃO COGNITO =====
COGNITO_USER_POOL_ID=us-east-1_xxxxx
COGNITO_CLIENT_ID=abc123def456
COGNITO_CLIENT_SECRET=your_client_secret_here

# ===== DEBUG/DESENVOLVIMENTO =====
USE_LOCALSTACK=false
# Defina como 'true' para usar LocalStack em desenvolvimento local
```

### Descrição das Variáveis

| Variável | Obrigatório | Padrão | Descrição |
|----------|-----------|--------|-----------|
| `AWS_ACCESS_KEY_ID` | Sim (produção) | - | Chave de acesso AWS |
| `AWS_SECRET_ACCESS_KEY` | Sim (produção) | - | Chave secreta AWS |
| `AWS_DEFAULT_REGION` | Não | `us-east-1` | Região AWS |
| `QUEUE_URL` | Não | `FILA-MONITORAMENTO-IDOSOS` | URL ou nome da fila SQS |
| `BUCKET_NAME` | Não | `bucket-videos-monitoramento` | Bucket S3 para vídeos |
| `COGNITO_USER_POOL_ID` | Sim (com API) | - | ID do User Pool Cognito |
| `COGNITO_CLIENT_ID` | Sim (com API) | - | ID da aplicação no Cognito |
| `COGNITO_CLIENT_SECRET` | Sim (com API) | - | Secret da aplicação no Cognito |
| `USE_LOCALSTACK` | Não | `false` | Usar LocalStack para AWS local |

### Exemplo para Desenvolvimento Local

```bash
# .env para usar LocalStack
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
USE_LOCALSTACK=true
QUEUE_URL=FILA-MONITORAMENTO-IDOSOS
```

### Exemplo para Produção AWS

```bash
# .env para AWS real
AWS_ACCESS_KEY_ID=${seu_access_key}
AWS_SECRET_ACCESS_KEY=${seu_secret_key}
AWS_DEFAULT_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_abc123xyz
COGNITO_CLIENT_ID=def456abc123def456abc123
COGNITO_CLIENT_SECRET=seu_client_secret_altamente_secreto
QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789/FILA-MONITORAMENTO-IDOSOS
BUCKET_NAME=meu-bucket-producao
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 📦 Dependências

Todas as dependências estão em [requirements.txt](requirements.txt). As principais incluem:

| Pacote | Finalidade |
|--------|-----------|
| ultralytics | YOLO para detecção de pose |
| opencv-python | Processamento de vídeo |
| fastapi | Framework API REST |
| uvicorn | Servidor ASGI |
| boto3 | Integração AWS |
| python-jose | Validação JWT |
| SpeechRecognition | Transcrição de áudio |
| moviepy | Extração de áudio |
| openai-whisper | Transcrição avançada (opcional) |
| transformers | Modelos NLP |
| librosa | Processamento de áudio |
| python-dotenv | Variáveis de ambiente |

## 💻 Uso

### Opção 1: Scripts Locais (Desenvolvimento Rápido)

#### Detecção de Quedas

1. Coloque seu vídeo como `video.mp4` no diretório do projeto
2. Execute o script:
```bash
python processors/fall_detection.py
```

3. Controles durante execução:
   - Pressione `q` para sair
   - O sistema mostrará em tempo real os alertas

**Estados do sistema:**
- 🟢 **MONITORANDO: TUDO OK** - Pessoa em pé, movimento normal
- 🟡 **ANALISANDO MOVIMENTO...** - Possível queda detectada, aguardando confirmação
- 🔴 **ALERTA: QUEDA DETECTADA!** - Queda confirmada, precisa de ajuda
- 🟢 **SEGURO: ACOMPANHADO** - Mais de uma pessoa na cena

#### Transcrição de Vídeo

1. Coloque seu vídeo como `video1.mp4` no diretório do projeto
2. Execute o script:
```bash
python processors/transcribe_video.py
```

3. A transcrição será salva em `temp_processing/transcription.txt`

**Nota**: Requer conexão com internet para usar o Google Speech Recognition API.

### Opção 2: API REST com FastAPI (Recomendado para Produção)

#### Iniciar o Servidor

```bash
# Ativar ambiente virtual (se ainda não estiver)
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # macOS/Linux

# Iniciar API
python api.py
```

O servidor estará disponível em: `http://localhost:8000`

#### Documentação Interativa da API

Após iniciar o servidor, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Endpoints Disponíveis

##### 1. Health Check
```bash
curl http://localhost:8000/health
```

Resposta:
```json
{"status": "healthy"}
```

##### 2. Login (Autenticação Cognito)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seu_usuario",
    "password": "sua_senha"
  }'
```

Resposta:
```json
{
  "AccessToken": "eyJhbGc...",
  "IdToken": "eyJhbGc...",
  "RefreshToken": "...",
  "ExpiresIn": 3600,
  "TokenType": "Bearer"
}
```

##### 3. Analisar Vídeo
```bash
curl -X POST http://localhost:8000/analyze-video \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ID_TOKEN" \
  -d '{
    "video_key": "video.mp4",
    "use_s3": false,
    "use_localstack": false
  }'
```

**Parâmetros:**
- `video_key` (string): Nome do arquivo (local ou no S3)
- `use_s3` (boolean): Se deve tentar baixar do S3
- `use_localstack` (boolean): Se deve usar LocalStack

**Resposta:**
```json
{
  "video_file": "video.mp4",
  "fall_detected": false,
  "confidence_score": 0.95,
  "transcription": "Texto transcrito do áudio...",
  "sentiment_analysis": {
    "emotion": "neutral",
    "confidence": 0.87
  },
  "alert_sent_to_sqs": false,
  "processing_time_seconds": 45.3
}
```

### Opção 3: Docker Compose com LocalStack (Desenvolvimento Completo)

```bash
# Iniciar LocalStack e todos os serviços
docker-compose -f docker/docker-compose.yml up -d

# Logs em tempo real
docker-compose -f docker/docker-compose.yml logs -f

# Parar tudo
docker-compose -f docker/docker-compose.yml down
```

LocalStack estará disponível em: `http://localhost:4566`

Seria necessário também:
- Executar `docker/localstack-init/create_queues.sh` para criar as filas
- Configurar as variáveis de ambiente com `USE_LOCALSTACK=true`

## ⚙️ Configuração Avançada

### Ajustar Sensibilidade da Detecção de Quedas

Edite as constantes em [processors/fall_detection.py](processors/fall_detection.py):

```python
# Frames necessários para confirmar queda
FRAMES_PARA_CONFIRMAR = 5      # Diminua para detectar mais rápido

# Frames necessários para resetar após queda
FRAMES_PARA_RECUPERAR = 60     # Aumente para evitar resets prematuros

# Limiares de detecção YOLOv8
conf=0.6    # Confiança mínima (0.5-0.8 recomendado)
iou=0.4     # IoU para NMS (0.3-0.5 recomendado)

# Limiares de aspecto corporal
MIN_ASPECT_RATIO = 0.5    # Pessoa mais larga que alta = caída
MAX_ASPECT_RATIO = 0.8    # Pessoa em pé = mais alta que larga
```

### Alterar Idioma da Transcrição

Em [processors/transcribe_video.py](processors/transcribe_video.py), edite a linha com `recognize_google`:

```python
text = recognizer.recognize_google(audio, language="pt-BR")
# Idiomas suportados:
# "en-US" (English)
# "es-ES" (Español)
# "fr-FR" (Français)
# "de-DE" (Deutsch)
# "it-IT" (Italiano)
# "ja-JP" (日本語)
# "zh-CN" (中文)
```

### Configuração do Whisper (Alternativa ao Google Speech)

Se preferir usar OpenAI Whisper em vez do Google Speech Recognition:

```python
import whisper

model = whisper.load_model("base")  # small, medium, large
result = model.transcribe("audio.wav", language="pt")
text = result["text"]
```

## 🧠 Algoritmo Detalhado de Detecção de Quedas

O sistema usa uma **máquina de estados com 3 estados principais**:

```
┌──────────┐
│  NORMAL  │ (Pessoa em pé, monitoramento contínuo)
└────┬─────┘
     │ Detecta indicadores de queda
     ↓
┌──────────┐
│ SUSPEITA │ (Aguardando confirmação, 5 frames)
└────┬─────┘
     │ Confirmado 5 frames/frames consecutivos?
     ├─ SIM → ┌────────┐
     │        │ CAIU   │ (Alerta, 60 frames)
     │        └────┬───┘
     │             │ 60 frames em pé?
     └─ NÃO ───────┘ Retorna NORMAL
```

### Critérios de Detecção

O sistema analisa múltiplos critérios:

| Critério | Threshold | Descrição |
|----------|-----------|-----------|
| Aspect Ratio | > 1.0 | Corpo mais largo que alto |
| Altura Ombros | < 60% frame | Ombros muito baixos |
| Altura Quadril | < 60% frame | Quadril muito baixo |
| Velocidade Descida | > 25 px/frame | Movimento rápido para baixo |
| Coincidência Keypoints | +90% | Múltiplos sinais confirmam queda |

## 📊 Estrutura do Projeto

```
ai-patient-monitor/
├── 📄 api.py                          # API FastAPI principal
├── 📄 README.md                       # Este arquivo
├── 📄 requirements.txt                # Dependências Python
├── 📄 setup_instructions.md           # Instruções detalhadas
│
├── 📁 processors/                     # Processadores de IA
│   ├── fall_detection.py              # Detecção de quedas com YOLOv8
│   ├── transcribe_video.py            # Transcrição de áudio
│   ├── analyze_multimodal_ai.py       # Análise multimodal (vídeo+áudio)
│   └── text_processor.py              # Processamento de texto
│
├── 📁 orchestrator/                   # Orquestração de pipeline
│   ├── cloud_orchestrator.py          # Coordenação do processamento em nuvem
│   └── mestro.py                      # Maestro para orquestração
│
├── 📁 aws_client/                     # Integração AWS
│   └── aws_integration.py             # Cliente SQS, S3
│
├── 📁 config/                         # Configurações
│   ├── load_envs.py                   # Carregamento de variáveis de ambiente
│   └── pipeline_config.py             # Configuração do pipeline
│
├── 📁 singletons/                     # Padrões Singleton
│   └── singletons.py                  # Instâncias únicas
│
├── 📁 docker/                         # Docker & LocalStack
│   ├── docker-compose.yml             # Orquestração de containers
│   └── localstack-init/               # Scripts de inicialização
│
├── 📁 terraform/                      # Infrastructure as Code (AWS)
│   ├── main.tf                        # Recursos S3, SQS
│   ├── variables.tf                   # Variáveis
│   └── terraform.tfvars               # Valores de entrada
│
├── 📁 temp_processing/                # Vídeos e áudios temporários
│   └── transcription.txt              # Resultado da transcrição
│
└── 🤖 yolov8n-pose.pt                 # Modelo YOLO (baixado automaticamente)
```

## 🔧 Troubleshooting

### ❌ Problema: "CUDA out of memory"
**Solução**: Use um modelo YOLO menor
```bash
# Em fall_detection.py, altere:
model = YOLO("yolov8n-pose.pt")  # nano
# para:
model = YOLO("yolov8s-pose.pt")  # small
```

### ❌ Problema: "ModuleNotFoundError: No module named 'cv2'"
**Solução**: Reinstale as dependências
```bash
pip install --upgrade opencv-python
# ou completo:
pip install -r requirements.txt --force-reinstall
```

### ❌ Problema: Google Speech Recognition retorna erro
**Solução**: Verifique conexão internet ou use Whisper offline
```bash
pip install openai-whisper
# Use whisper em vez de google speech recognition
```

### ❌ Problema: "Token expirado" no Cognito
**Solução**: Faça login novamente para obter novo token
```bash
# Ou use o RefreshToken para renovar
```

### ❌ Problema: LocalStack não conecta
**Solução**: Verifique se está rodando e acessível
```bash
curl http://localhost:4566/_localstack/health
# Se falhar, reinicie:
docker-compose -f docker/docker-compose.yml restart
```

## 📚 Recursos Adicionais

- **YOLO Documentação**: https://docs.ultralytics.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **AWS Cognito**: https://docs.aws.amazon.com/cognito/
- **LocalStack**: https://docs.localstack.cloud/
- **Terraform AWS**: https://registry.terraform.io/providers/hashicorp/aws/latest

## 🔐 Segurança

### Boas Práticas
1. ✅ Nunca commite `.env` no Git (já está em `.gitignore`)
2. ✅ Use secrets seguros para `COGNITO_CLIENT_SECRET`
3. ✅ Ative HTTPS em produção
4. ✅ Rotacionepredere chaves AWS regularmente
5. ✅ Monitore logs do CloudWatch
6. ✅ Use VPC e Security Groups na AWS

### Proteção da API
- Token JWT do Cognito obrigatório
- Validação de issuer e audience
- Tokens com expiração (3600s padrão)
- Refresh tokens para renovação

## 🤝 Contribuindo

1. Crie uma branch: `git checkout -b feature/sua-feature`
2. Commit: `git commit -am 'Add feature'`
3. Push: `git push origin feature/sua-feature`
4. Abra um Pull Request

## 📝 Licença

Licença MIT - Veja o arquivo LICENSE para detalhes complementares.

## 🐛 Reportar Problemas

Se encontrou um bug ou tem uma sugestão de melhoria, abra uma [Issue](../../issues).

## 📬 Suporte

Para dúvidas ou suporte, entre em contato através de:
- Issues do GitHub
- Documentação detalhada em [setup_instructions.md](setup_instructions.md)

---

**Desenvolvido com ❤️ para monitoramento inteligente de pacientes**

Última atualização: Fevereiro 2026
