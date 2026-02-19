from config.pipeline_config import PipelineConfig
from processors.text_processor import transcribe_audio
from processors.analyze_multimodal_ai import analyze_multimodal_ai
# ==============================================================================
# CAMADA 4: ORQUESTRADOR PRINCIPAL (MAESTRO)
# ==============================================================================
config = PipelineConfig()

audio_file = config.base_dir / 'Video_Deitado_Gritando_Socorro.mp4'


if not audio_file.exists():
    print(f"❌ Arquivo não encontrado: {audio_file}")

else:
    print("-" * 50)

    # 1. Transcrição e Persistência
    text_en = transcribe_audio(audio_file, config.whisper_model)
    print(f"📝 Texto original (EN): {text_en}")

    # # 3. Análise Multimodal (Texto + Som)
    analyze_multimodal_ai(text_en, audio_file)
    print("-" * 50)
