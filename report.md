# Relatório Técnico: Sistema de Monitoramento Multimodal de Pacientes com IA

## 1. Descrição do Fluxo Multimodal

O sistema opera através de uma arquitetura de orquestração em nuvem (`cloud_orchestrator.py`) que integra três fluxos de dados distintos (Vídeo, Áudio e Texto) para tomar decisões complexas sobre o estado do paciente.

### Etapas do Processamento:
1.  **Ingestão**: O sistema recebe uma solicitação via API (`api.py`) contendo a chave de um vídeo (S3 ou local).
2.  **Aquisição**: O orquestrador baixa o vídeo e separa o fluxo de áudio.
3.  **Processamento Paralelo**:
    *   **Visual**: O vídeo é analisado quadro a quadro para estimativa de pose.
    *   **Áudio (Sinal)**: O áudio bruto passa por processamento digital de sinais (DSP) para análise de energia.
    *   **Áudio (Semântico)**: O áudio é transcrito para texto (Speech-to-Text).
4.  **Inferência de IA**: Modelos específicos classificam emoções no áudio e no texto transcrito.
5.  **Fusão de Sensores**: O módulo `analyze_multimodal_ai.py` combina os resultados visuais, acústicos e semânticos.
6.  **Decisão e Alerta**: Com base na gravidade combinada, o sistema envia alertas para uma fila SQS (AWS) com prioridades definidas (Crítica ou Média).

---

## 2. Modelos e Algoritmos Aplicados

O sistema utiliza uma abordagem híbrida combinando Deep Learning e algoritmos heurísticos determinísticos.

### A. Visão Computacional (Vídeo)
*   **Modelo**: **YOLOv8-Pose** (`yolov8n-pose.pt`).
*   **Função**: Detecção de pessoas e extração de esqueleto (Keypoints: Nariz, Ombros, Quadris).
*   **Lógica de Negócio**: Máquina de Estados Finitos (Normal -> Suspeita -> Queda).
    *   *Critérios*: Aspect Ratio do Bounding Box, alinhamento vertical de ombros/quadris e velocidade de descida do eixo Y (nariz).

### B. Processamento de Áudio (DSP e IA)
*   **Processamento de Sinal (DSP)**: Biblioteca **Librosa**.
    *   Cálculo de Energia RMS (Root Mean Square) para detectar picos de volume.
    *   Análise temporal para diferenciar impactos (curta duração < 0.3s) de gritos (longa duração > 0.5s).
*   **Classificação de Emoção em Áudio**: Modelo de Deep Learning (via Singleton `get_audio_analysis_model`).
    *   Detecta nuances na tonalidade da voz (ex: Medo, Choro).

### C. Processamento de Linguagem Natural (Texto)
*   **Transcrição**: **OpenAI Whisper** ou Google Speech Recognition.
*   **Análise de Sentimento**: Modelo Transformer (via Singleton `get_text_analysis_model`).
    *   Analisa o conteúdo semântico da fala (ex: "Socorro", "Dói").

---

## 3. Resultados e Detecção de Anomalias

O sistema é capaz de diferenciar falsos positivos de emergências reais através da correlação de dados (Requisito 63).

### Matriz de Decisão (Fusão de Dados)

| Cenário | Visual (YOLO) | Áudio (DSP) | Semântica (IA) | Classificação do Sistema | Ação |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Queda Silenciosa** | Queda Detectada | Silêncio | N/A | **Emergência Crítica** | Alerta SQS (High) |
| **Queda com Grito** | Queda Detectada | Alta Energia (>0.5s) | "Socorro!" (Medo) | **Emergência Crítica (Confirmada)** | Alerta SQS (High) |
| **Objeto Caindo** | Normal | Impacto (<0.3s) | N/A | **Falso Positivo** | Ignorar |
| **Angústia** | Normal | Choro | "Estou triste" (Tristeza) | **Risco Emocional** | Alerta SQS (Medium) |

### Exemplos de Anomalias Detectadas

#### 1. Detecção de Queda Física (`fall_detection.py`)
O algoritmo detecta uma anomalia quando:
*   O `aspect_ratio` do corpo torna-se > 1.0 (pessoa na horizontal).
*   A velocidade vertical do nariz excede 25 pixels/frame.
*   **Resultado**: Transição de estado para `ESTADO_CAIU` e flag `fall_detected = True`.

#### 2. Detecção de Emergência Vocal (`analyze_multimodal_ai.py`)
O sistema analisa a energia do áudio:
*   **Impacto Físico**: Pico de energia RMS > 0.05 com duração < 0.3s.
*   **Grito de Socorro**: Pico de energia RMS > 0.05 com duração sustentada >= 0.5s.
*   **Resultado**: Flags `is_impact` ou `is_sustained_emergency` acionadas.

#### 3. Risco Emocional
Mesmo sem eventos físicos, o sistema monitora o bem-estar:
*   Se o modelo de texto ou áudio detectar `["fear", "sadness", "anger"]`.
*   **Resultado**: Flag `has_emotional_risk` aciona um alerta preventivo de saúde mental.

---

## 4. Conclusão Técnica

O sistema atinge robustez ao não depender de um único sensor. A implementação do **Requisito 63** (análise multimodal) permite:
1.  Redução de falsos positivos (ex: barulho de objeto caindo não gera alerta de queda se o visual estiver normal).
2.  Cobertura de casos extremos (ex: queda fora do campo de visão da câmera pode ser inferida por um grito de socorro sustentado).
3.  Priorização inteligente de alertas para a equipe médica.
```

<!--
[PROMPT_SUGGESTION]Crie um diagrama Mermaid no arquivo markdown ilustrando o fluxo de decisão multimodal.[/PROMPT_SUGGESTION]
[PROMPT_SUGGESTION]Adicione testes unitários para a função analyze_multimodal_ai simulando diferentes cenários de input.[/PROMPT_SUGGESTION]
