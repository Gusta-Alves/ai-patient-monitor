# Sistema de Monitoramento Inteligente

Sistema de detecção de quedas e transcrição de vídeo usando IA para monitoramento de pacientes.

## 📋 Funcionalidades

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

## 📦 Dependências

- **ultralytics**: Framework YOLO para detecção de objetos e pose estimation
- **opencv-python**: Processamento de imagem e vídeo
- **moviepy**: Manipulação e extração de áudio de vídeos
- **SpeechRecognition**: Transcrição de áudio para texto

## 💻 Uso

### Detecção de Quedas

1. Coloque seu vídeo como `video.mp4` no diretório do projeto
2. Execute o script:
```bash
python fall_detection.py
```

3. Controles:
   - Pressione `q` para sair
   - O sistema mostrará em tempo real:
     - Status de monitoramento
     - Alertas de queda
     - Indicador de assistência (múltiplas pessoas)

**Estados do sistema:**
- 🟢 **MONITORANDO: TUDO OK** - Pessoa em pé, movimento normal
- 🟡 **ANALISANDO MOVIMENTO...** - Possível queda detectada, aguardando confirmação
- 🔴 **ALERTA: QUEDA DETECTADA!** - Queda confirmada, precisa de ajuda
- 🟢 **SEGURO: ACOMPANHADO** - Mais de uma pessoa na cena

### Transcrição de Vídeo

1. Coloque seu vídeo como `video1.mp4` no diretório do projeto
2. Execute o script:
```bash
python transcribe_video.py
```

3. A transcrição será salva em `transcricao1.txt`

**Nota**: Requer conexão com internet para usar o Google Speech Recognition API.

## ⚙️ Configuração

### Ajustar sensibilidade da detecção de quedas

Edite as constantes em `fall_detection.py`:

```python
# Frames necessários para confirmar queda
FRAMES_PARA_CONFIRMAR = 5      # Diminua para detectar mais rápido

# Frames necessários para resetar após queda
FRAMES_PARA_RECUPERAR = 60     # Aumente para evitar resets prematuros

# Limiares de detecção
conf=0.6    # Confiança mínima (0.5-0.8 recomendado)
iou=0.4     # IoU para NMS (0.3-0.5 recomendado)
```

### Alterar idioma da transcrição

Em `transcribe_video.py`, linha 17:
```python
text = recognizer.recognize_google(audio, language="pt-BR")  # Alterar para "en-US", "es-ES", etc.
```

## 🏗️ Estrutura do Projeto

```
.
├── fall_detection.py          # Sistema de detecção de quedas
├── transcribe_video.py        # Sistema de transcrição de vídeo
├── requirements.txt           # Dependências do projeto
├── README.md                  # Documentação
├── .gitignore                # Arquivos ignorados pelo Git
├── yolov8n-pose.pt           # Modelo YOLO (baixar separadamente)
└── .venv/                    # Ambiente virtual (não versionado)
```

## 🎯 Algoritmo de Detecção de Quedas

O sistema usa uma **máquina de estados com 3 estados**:

1. **NORMAL**: Pessoa em pé, monitoramento contínuo
2. **SUSPEITA**: Indicadores de queda detectados, aguardando confirmação (5 frames)
3. **CAIU**: Queda confirmada, alerta mantido até recuperação (60 frames em pé)

**Critérios de detecção:**
- Aspect ratio > 1.0 (corpo mais largo que alto)
- Ombros e quadris na mesma altura vertical
- Velocidade de descida > 25 pixels/frame
- Posição baixa (nariz abaixo de 60% da altura do frame)

## 📝 Licença

[Especifique sua licença aqui]

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 🐛 Problemas Conhecidos

- A transcrição requer conexão com internet
- Vídeos muito longos podem consumir muita memória
- O modelo YOLO pode ter falsos positivos em cenários com muita movimentação

## 📧 Contato

[Adicione suas informações de contato]
