# Instruções de Setup do Ambiente

## Para novos desenvolvedores

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd "fase 4 - pos/Aula 4"
```

### 2. Configure o ambiente virtual

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Baixe o modelo YOLO

O modelo será baixado automaticamente na primeira execução de `fall_detection.py`.

Alternativamente, baixe manualmente:
```bash
# Crie o diretório se necessário
mkdir -p models

# Download via wget ou curl
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-pose.pt
```

### 4. Adicione seus vídeos de teste

```bash
# Coloque seus vídeos no diretório raiz
# Arquivos esperados:
# - video.mp4 (para fall_detection.py)
# - video1.mp4 (para transcribe_video.py)
```

### 5. Teste a instalação

```bash
# Teste a detecção de quedas
python fall_detection.py

# Teste a transcrição (requer internet)
python transcribe_video.py
```

## Estrutura do Ambiente Virtual

Após a instalação, você terá:
```
.venv/
├── bin/ (ou Scripts/ no Windows)
│   ├── python
│   ├── pip
│   └── activate
├── lib/
│   └── python3.x/
│       └── site-packages/
│           ├── cv2/
│           ├── ultralytics/
│           ├── moviepy/
│           ├── speech_recognition/
│           └── ...
└── pyvenv.cfg
```

## Verificar Instalação

```bash
# Ativar ambiente
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate  # Windows

# Verificar pacotes instalados
pip list

# Verificar versões específicas
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import ultralytics; print('Ultralytics:', ultralytics.__version__)"
python -c "import moviepy; print('MoviePy:', moviepy.__version__)"
python -c "import speech_recognition; print('SpeechRecognition:', speech_recognition.__version__)"
```

## Troubleshooting

### Erro: "No module named 'cv2'"
```bash
pip install opencv-python --force-reinstall
```

### Erro: "No module named 'moviepy'"
```bash
pip install moviepy --upgrade
```

### Erro: YOLO model download failed
Baixe manualmente de: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-pose.pt

### Erro: Speech recognition não funciona
- Verifique conexão com internet
- Teste o microfone: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`

## Atualizando Dependências

```bash
# Atualizar todas as dependências
pip install --upgrade -r requirements.txt

# Atualizar pacote específico
pip install --upgrade ultralytics

# Gerar novo requirements.txt (após adicionar novos pacotes)
pip freeze > requirements.txt
```

## Desativar Ambiente Virtual

```bash
deactivate
```
