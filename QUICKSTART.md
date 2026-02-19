# 🚀 Quick Start Guide - AI Patient Monitor

Guia rápido para colocar o sistema rodando em 5 minutos.

## Option 1️⃣: Teste Rápido (Sem AWS) - 2 minutos ⚡

```bash
# 1. Clone e entre na pasta
git clone <repo-url>
cd ai-patient-monitor

# 2. Crie ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou: source .venv/bin/activate  # macOS/Linux

# 3. Instale dependências
pip install -r requirements.txt

# 4. Coloque um vídeo de teste
# Copie video.mp4 para a raiz do projeto

# 5. Execute detecção de quedas
python processors/fall_detection.py

# Pronto! Você verá a detecção em tempo real
```

## Option 2️⃣: Com API REST - 5 minutos 🔌

```bash
# Siga os passos 1-3 acima, depois:

# 4. Configure variáveis de ambiente
# Copie .env.example para .env e edite (opcional para teste)
copy .env.example .env

# 5. Inicie a API
python api.py

# 6. Acesse em seu navegador
# - Documentação: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
```

## Option 3️⃣: Com LocalStack (Desenvolvimento Completo) - 10 minutos 🐳

```bash
# Siga os passos 1-3 acima, depois:

# 4. Inicie LocalStack (precisa Docker)
docker-compose -f docker/docker-compose.yml up -d

# 5. Configure .env para LocalStack
# Edite .env e defina:
# - USE_LOCALSTACK=true
# - AWS_ACCESS_KEY_ID=test
# - AWS_SECRET_ACCESS_KEY=test

# 6. Inicie a API
python api.py

# 7. Teste com LocalStack
# - LocalStack UI: http://localhost:4566
# - API Docs: http://localhost:8000/docs
```

## Testando a API com curl

```bash
# 1. Health Check
curl http://localhost:8000/health

# 2. Analisar vídeo local
curl -X POST http://localhost:8000/analyze-video \
  -H "Content-Type: application/json" \
  -d '{
    "video_key": "video.mp4",
    "use_s3": false,
    "use_localstack": false
  }'
```

## Arquivos Importantes

- 📄 **README.md** - Documentação completa
- ⚙️ **.env.example** - Modelo de variáveis de ambiente
- 📋 **requirements.txt** - Dependências Python
- 🐳 **docker-compose.yml** - Configuração Docker
- 📚 **setup_instructions.md** - Instruções detalhadas

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` | Execute `pip install -r requirements.txt` novamente |
| `permission denied` (Mac/Linux) | Execute `chmod +x .venv/bin/activate` |
| Docker não conecta | Verifique se Docker Desktop está rodando |
| Porta 8000 em uso | Mude em `api.py`: `uvicorn.run(app, port=8001)` |
| Sem câmera/vídeo | Coloque video.mp4 na raiz do projeto |

## Contatos e Suporte

- 📖 Documentação: Veja [README.md](README.md)
- 🐛 Issues: GitHub Issues seção
- 💬 Discussões: GitHub Discussions

---

**Desenvolvido com ❤️ para monitoramento inteligente de pacientes**

Última atualização: Fevereiro 2026
