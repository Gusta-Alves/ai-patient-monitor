import os
import json
import boto3
from pathlib import Path
from aws_client.aws_integration import SQSClient
from processors.fall_detection import analyze_video_file
from processors.analyze_multimodal_ai import analyze_multimodal_ai
from processors.transcribe_video import extract_audio_from_video
from processors.transcribe_video import transcribe_audio_to_text
# Configurações
QUEUE_URL = os.getenv("QUEUE_URL", "FILA-MONITORAMENTO-IDOSOS")
BUCKET_NAME = "bucket-videos-monitoramento"
TEMP_DIR = Path("./temp_processing")


def download_video(video_filename, use_s3=False, use_localstack=False):
    """
    Gerencia o download do vídeo.
    Se use_s3=True, tenta baixar do bucket.
    Se falhar ou use_s3=False, usa o arquivo local (Mock).
    """
    target_path = TEMP_DIR / video_filename

    if use_s3:
        try:
            print(
                f"📥 [S3] Tentando baixar {video_filename} do bucket {BUCKET_NAME}...")
            
            if use_localstack:
                print(f"📥 Using Local stack...")
                s3 = boto3.client('s3', region_name='us-east-1', endpoint_url="http://localhost:4566")
            else:
                s3 = boto3.client('s3', region_name='us-east-1')

            s3.download_file(BUCKET_NAME, video_filename, str(target_path))
            print("✅ Download do S3 concluído com sucesso.")
            return target_path
        except Exception as e:
            print(f"⚠️ [S3] Falha no download ou cliente não configurado: {e}")
            print("🔄 Revertendo para arquivo LOCAL...")

    # Lógica de Fallback para arquivo local
    print(f"📥 [LOCAL] Buscando arquivo: {video_filename}...")
    local_path = Path(os.path.abspath(video_filename))

    if local_path.exists():
        return local_path
    elif target_path.exists():
        return target_path

    raise FileNotFoundError(
        f"Arquivo {video_filename} não encontrado localmente nem no S3.")


def process_patient_video(video_key, use_s3=False, use_localstack=False, headless=True):
    """
    Função principal que seria acionada por um Lambda ou Loop de Polling
    """

    try:
        # 1. Setup do ambiente
        TEMP_DIR.mkdir(exist_ok=True)
        video_path = download_video(video_key, use_s3=use_s3, use_localstack=use_localstack)
        audio_path = TEMP_DIR / "extracted_audio.wav"

        print(f"⚙️ Iniciando análise multimodal para: {video_key}")

        # 2. Análise Visual (Detecção de Queda - YOLO)
        # Headless = True para não abrir janelas no servidor
        fall_detected = analyze_video_file(
            str(video_path), headless=headless)
        print(
            f"📹 [VIDEO] Resultado da Análise Visual: {'🚨 QUEDA DETECTADA' if fall_detected else '✅ Movimento Normal'}")

        # 3. Extração e Transcrição de Áudio
        extract_audio_from_video(str(video_path), str(audio_path))

        # Usando speech_recognition simples (pode ser substituído pelo Whisper do mestro.py)
        # Para simplificar, vamos assumir que temos o texto ou usar o mock
        # Aqui estou chamando a função existente, mas ela imprime.
        # Idealmente, transcribe_audio_to_text deveria retornar a string.
        # Vamos assumir um texto mockado para teste se a transcrição falhar ou demorar
        text_content = transcribe_audio_to_text(
            str(audio_path), str(TEMP_DIR / "transcription.txt"))

        # 4. Análise de Áudio e Emoção
        ai_analysis = analyze_multimodal_ai(text_content, audio_path)

        if not ai_analysis:
            print("❌ Falha na análise de áudio.")
            return

        # ======================================================================
        # LÓGICA DE DECISÃO UNIFICADA (FUSÃO DE SENSORES)
        # ======================================================================

        alert_payload = {}
        priority = "low"

        # CASO 1: EMERGÊNCIA CRÍTICA (Queda Visual OU Grito/Impacto Sonoro)
        if fall_detected or ai_analysis['is_impact'] or ai_analysis['is_sustained_emergency']:
            priority = "critical"
            reason = []
            if fall_detected:
                reason.append("QUEDA VISUAL (YOLO)")
            if ai_analysis['is_impact']:
                reason.append("IMPACTO SONORO")
            if ai_analysis['is_sustained_emergency']:
                reason.append("GRITO/SOCORRO")

            alert_payload = {
                "alert_type": "EMERGENCY_FALL",
                "message": f"🚨 SOCORRO: Evento crítico detectado! Motivos: {', '.join(reason)}",
                "metadata": {
                    "patient_id": "12345",
                    "location": "Quarto 101",
                    "evidence": ai_analysis
                }
            }

        # CASO 2: ATENÇÃO PSICOLÓGICA (Tristeza/Medo sem queda)
        elif ai_analysis['has_emotional_risk']:
            priority = "medium"
            alert_payload = {
                "alert_type": "EMOTIONAL_DISTRESS",
                "message": f"⚠️ ATENÇÃO: Paciente demonstra {ai_analysis['text_emotion']} / {ai_analysis['audio_emotion']}",
                "metadata": {
                    "patient_id": "12345",
                    "transcription": ai_analysis['transcription']
                }
            }

        # Envio para SQS
        if alert_payload:
            print(
                f"📤 Enviando alerta [{priority.upper()}]: {alert_payload['message']}")
            
            # Usa a classe SQSClient corrigida e simplificada
            # Ela já resolve a URL e cria a fila no LocalStack se necessário
            sqs = SQSClient(QUEUE_URL, useLocalStack=use_localstack)
            sqs.send_alert(
                alert_payload['alert_type'], 
                alert_payload['message'], 
                alert_payload['metadata']
            )
            
            return {
                "status": "alert_sent",
                "priority": priority,
                "data": alert_payload
            }
        else:
            print("✅ Situação Normal. Nenhum alerta enviado.")
            return {
                "status": "normal",
                "message": "Nenhum risco detectado."
            }

    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        raise e
