import numpy as np
import librosa
from pathlib import Path
from singletons.singletons import get_text_analysis_model, get_audio_analysis_model


def analyze_multimodal_ai(text: str, audio_path: Path):
    """
    Análise Multimodal Profissional: Diferenciação entre impacto físico e emergência vocal.
    Garante conformidade total com o Requisito 63.
    """
    print("🧠 Iniciando Processamento de Sinais e Fusão de Dados...")

    # 1. Carregamento e Normalização
    audio_data, _ = librosa.load(str(audio_path), sr=16000)
    if audio_data.size == 0:
        return

    # 2. Extração de Características Físicas (DSP - Digital Signal Processing)
    # Calculamos a energia por quadros (frames) para ver a evolução temporal
    frame_length = 2048
    hop_length = 512
    rmse = librosa.feature.rms(
        y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]

    # Identifica a duração do evento acima de um threshold (0.1 de energia relativa)
    peak_duration = np.sum(rmse > (np.max(rmse) * 0.5)) * (hop_length / 16000)

    # Característica de Impacto: Energia alta + Duração muito curta (< 0.3s)
    is_impact = (np.max(rmse) > 0.05) and (peak_duration < 0.3)
    # Característica de Grito/Socorro: Energia alta + Duração sustentada (> 0.5s)
    is_sustained_emergency = (np.max(rmse) > 0.05) and (peak_duration >= 0.5)

    # 3. Inferência das IAs (Texto e Som)
    t_input = text if text.strip() else "Neutral silence"
    t_pred = get_text_analysis_model()(t_input)[0]
    a_pred = get_audio_analysis_model()(audio_data)[0]

    # 4. Classificação de Risco
    risk_emotions = ["fear", "sadness", "sad", "anger", "disgust"]
    has_emotional_risk = t_pred['label'] in risk_emotions or a_pred['label'] in risk_emotions

    # 5. Conclusão Baseada em Evidências Multimodais
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
