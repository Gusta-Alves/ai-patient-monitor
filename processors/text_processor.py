from pyannote.audio import Pipeline
import torch
from pathlib import Path
from functools import lru_cache
from singletons.singletons import get_whisper_model
import os
from dotenv import load_dotenv

project_root = Path(__file__).parent
load_dotenv(project_root / ".env")


@lru_cache(maxsize=1)
def get_diarization_pipeline():
    """Carrega o modelo após o aceite manual no site do Hugging Face"""
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token= os.getenv("HF_TOKEN"),
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return pipeline.to(device)


def transcribe_audio(audio_path: Path, model_name: str) -> str:
    """Transcreve e separa falas por locutor (Diarização)"""
    model = get_whisper_model(model_name)
    diarization_pipeline = get_diarization_pipeline()

    # 1. Transcrição com Whisper
    print(f"🎤 Transcrevendo áudio: {audio_path.name}...")
    result = model.transcribe(str(audio_path), verbose=False)
    segments = result.get("segments", [])

    # 2. Executa a Diarização
    print("👥 Identificando locutores...")
    diarization = diarization_pipeline(str(audio_path))

    final_transcript = []

    # 3. Cruzamento de Timestamps
    for segment in segments:
        start, end = segment['start'], segment['end']
        text = segment['text'].strip()

        speaker = "Unknown"

        # AJUSTE: O itertracks() pertence ao objeto retornado pela pipeline
        # Na versão 3.1, se 'diarization' vier como DiarizeOutput, acessamos itertracks() assim:
        try:
            for turn, _, speaker_label in diarization.itertracks(yield_label=True):
                if turn.start <= start <= turn.end:
                    speaker = speaker_label
                    break
        except AttributeError:
            # Fallback caso a estrutura mude em atualizações menores
            speaker = "Speaker_Detected"

        final_transcript.append(f"[{speaker}]: {text}")

    return "\n".join(final_transcript)
