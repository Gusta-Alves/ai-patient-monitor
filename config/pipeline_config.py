from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    """Configurações centrais do Pipeline de IA"""
    base_dir: Path = Path(".")
    text_output_path: Path = Path("transcription.txt")
    translated_output_path: Path = Path("transcription_pt.txt")
    whisper_model: str = "base"
    translate_target: str = "pt"
