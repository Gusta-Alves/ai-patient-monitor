import numpy as np
import librosa
from pathlib import Path
from singletons.singletons import get_text_analysis_model, get_audio_analysis_model


def analyze_multimodal_ai(text: str, audio_path: Path):
    print("🧠 Iniciando Processamento de Sinais e Fusão de Dados...")
    audio_data, _ = librosa.load(str(audio_path), sr=16000)
    if audio_data.size == 0:
        return None
    frame_length = 2048
    hop_length = 512
    rmse = librosa.feature.rms(
        y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
    peak_duration = np.sum(rmse > (np.max(rmse) * 0.5)) * (hop_length / 16000)
    is_impact = (np.max(rmse) > 0.05) and (peak_duration < 0.3)
    is_sustained_emergency = (np.max(rmse) > 0.05) and (peak_duration >= 0.5)
    t_input = text if text.strip() else "Neutral silence"
    t_pred = get_text_analysis_model()(t_input)[0]
    a_pred = get_audio_analysis_model()(audio_data)[0]
    risk_emotions = ["fear", "sadness", "sad", "anger", "disgust"]
    has_emotional_risk = t_pred['label'] in risk_emotions or a_pred['label'] in risk_emotions
    result = {
        "is_impact": bool(is_impact),
        "is_sustained_emergency": bool(is_sustained_emergency),
        "has_emotional_risk": bool(has_emotional_risk),
        "text_emotion": t_pred['label'],
        "audio_emotion": a_pred['label'],
        "transcription": text
    }
    print(f"\n📊 LAUDO TÉCNICO MULTIMODAL")
    if is_impact:
        print("🚨 TIPO DE EVENTO: IMPACTO FÍSICO DETECTADO (QUEDA).")
    elif is_sustained_emergency:
        print("🚨 TIPO DE EVENTO: EMERGÊNCIA VOCAL SUSTENTADA (GRITO/SOCORRO).")
    if has_emotional_risk:
        print(
            f"⚠️ ESTADO EMOCIONAL: Risco detectado ({t_pred['label']}/{a_pred['label']}).")
    if is_impact or is_sustained_emergency or has_emotional_risk:
        print("\n✅ AÇÃO: Protocolo de emergência acionado via Requisito 63.")
    return result
