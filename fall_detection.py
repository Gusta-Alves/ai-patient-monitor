from ultralytics import YOLO
import cv2
from collections import deque
import time
from aws_client.aws_integration import SQSClient

QUEUE_URL = "FILA-TEST"
model = YOLO('yolov8n-pose.pt')
cap = cv2.VideoCapture("video.mp4")
client = SQSClient(QUEUE_URL, useLocalStack="true")

# Cooldown entre alertas (segundos)
COOLDOWN_SECONDS = 60
last_alert_time = 0
# ============================================================
# MAQUINA DE ESTADOS - evita ficar alternando entre estados
# ============================================================
ESTADO_NORMAL = "NORMAL"
ESTADO_SUSPEITA = "SUSPEITA"
ESTADO_CAIU = "CAIU"
COOLDOWN_SECONDS = 60  # ajuste conforme necessário
last_alert_time = 0
estado_atual = ESTADO_NORMAL

HISTORICO_TAMANHO = 10
historico_nariz_y = deque(maxlen=HISTORICO_TAMANHO)

frames_suspeita = 0
FRAMES_PARA_CONFIRMAR = 5

frames_recuperacao = 0
FRAMES_PARA_RECUPERAR = 60

# Variáveis auxiliares
prev_y_nariz = 0
frame_height = None


def alert_with_colldown(client, COOLDOWN_SECONDS, last_alert_time):
    now = time.time()
    if now - last_alert_time >= COOLDOWN_SECONDS:
        client.send_alert(
            alert_type="FALL_DETECTION",
            message="Uma queda foi detectada no quarto 101",
            metadata={"priority": "high", "patient_id": "12345"}
        )
        last_alert_time = now
    else:
        remaining = int(COOLDOWN_SECONDS - (now - last_alert_time))
        print(f"Alerta suprimido por cooldown ({remaining}s restantes)")


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    if frame_height is None:
        frame_height = frame.shape[0]

    # conf=0.6 -> só aceita detecções com 60%+ de confiança
    # iou=0.4  -> suprime caixas muito sobrepostas (elimina duplicatas)
    results = model(frame, conf=0.6, iou=0.4, verbose=False)

    # ==========================================================
    # 1. REGRA: Se tem mais de 1 pessoa, está seguro
    # ==========================================================
    pessoas_detectadas = [
        box for box in results[0].boxes
        if box.cls == 0 and box.conf >= 0.6
    ]

    if len(pessoas_detectadas) > 1:
        estado_atual = ESTADO_NORMAL
        frames_suspeita = 0
        frames_recuperacao = 0
        cor = (0, 255, 0)  # Verde
        cv2.putText(frame, "SEGURO: ACOMPANHADO", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)

    elif len(pessoas_detectadas) == 1:
        # ==========================================================
        # 2. ANÁLISE DE QUEDA
        # ==========================================================
        tem_keypoints = (
            results[0].keypoints is not None
            and len(results[0].keypoints.xy) > 0
            and len(results[0].keypoints.xy[0]) > 0
        )

        indicadores_queda = False

        if tem_keypoints:
            keypoints = results[0].keypoints.xy[0]

            nariz_y = keypoints[0][1].item()
            ombro_esq_y = keypoints[5][1].item()
            ombro_dir_y = keypoints[6][1].item()
            quadril_esq_y = keypoints[11][1].item()
            quadril_dir_y = keypoints[12][1].item()

            media_ombros_y = (ombro_esq_y + ombro_dir_y) / 2
            media_quadril_y = (quadril_esq_y + quadril_dir_y) / 2

            # --- Critério 1: Aspect Ratio (bounding box mais larga que alta = deitado) ---
            box = pessoas_detectadas[0].xywh[0]
            w, h = box[2].item(), box[3].item()
            aspect_ratio = w / h if h > 0 else 0
            eh_deitado = aspect_ratio > 1.0

            # --- Critério 2: Ombros e quadris na mesma altura (corpo horizontal) ---
            diff_ombro_quadril = abs(media_ombros_y - media_quadril_y)
            corpo_horizontal = diff_ombro_quadril < (frame_height * 0.08)

            # --- Critério 3: Velocidade de descida (queda brusca) ---
            historico_nariz_y.append(nariz_y)
            velocidade = nariz_y - prev_y_nariz if prev_y_nariz > 0 else 0
            queda_rapida = velocidade > 25

            # --- Critério 4: Nariz abaixo de 60% da tela (está baixo) ---
            esta_baixo = nariz_y > (frame_height * 0.6)

            indicadores_queda = (
                (eh_deitado and esta_baixo)
                or (corpo_horizontal and esta_baixo)
                or (queda_rapida and esta_baixo)
            )

            prev_y_nariz = nariz_y

        # ==========================================================
        # 3. MÁQUINA DE ESTADOS
        # ==========================================================
        if estado_atual == ESTADO_NORMAL:
            if indicadores_queda:
                frames_suspeita += 1
                if frames_suspeita >= FRAMES_PARA_CONFIRMAR:
                    estado_atual = ESTADO_CAIU
                    frames_suspeita = 0
                    frames_recuperacao = 0
                else:
                    estado_atual = ESTADO_SUSPEITA
            else:
                frames_suspeita = 0

        elif estado_atual == ESTADO_SUSPEITA:
            if indicadores_queda:
                frames_suspeita += 1
                if frames_suspeita >= FRAMES_PARA_CONFIRMAR:
                    estado_atual = ESTADO_CAIU
                    frames_suspeita = 0
                    frames_recuperacao = 0
            else:
                frames_suspeita = 0
                estado_atual = ESTADO_NORMAL

        elif estado_atual == ESTADO_CAIU:
            if not indicadores_queda:
                frames_recuperacao += 1
                if frames_recuperacao >= FRAMES_PARA_RECUPERAR:
                    estado_atual = ESTADO_NORMAL
                    frames_recuperacao = 0
            else:
                # Ainda no chão, reseta recuperação
                frames_recuperacao = 0

        # ==========================================================
        # 4. EXIBIÇÃO
        # ==========================================================
        if estado_atual == ESTADO_CAIU:
            cv2.putText(frame, "ALERTA: QUEDA DETECTADA!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            cv2.putText(frame, "PACIENTE PRECISA DE AJUDA", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            alert_with_colldown(client, COOLDOWN_SECONDS, last_alert_time)
            cv2.rectangle(frame, (5, 5), (frame.shape[1] - 5, frame.shape[0] - 5),
                          (0, 0, 255), 4)

        elif estado_atual == ESTADO_SUSPEITA:
            cv2.putText(frame, "ANALISANDO MOVIMENTO...", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

        else:
            cv2.putText(frame, "MONITORANDO: TUDO OK", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)

    else:
        cv2.putText(frame, "NENHUMA PESSOA DETECTADA", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)

    cv2.imshow("Monitoramento Inteligente", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
