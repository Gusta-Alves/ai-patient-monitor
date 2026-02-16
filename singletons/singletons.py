import whisper
from functools import lru_cache
from transformers import pipeline


@lru_cache(maxsize=1)
def get_whisper_model(model_name: str):
    return whisper.load_model(model_name)


@lru_cache(maxsize=1)
def get_text_analysis_model():
    """Modelo DistilBERT para classificação de emoções em texto"""
    return pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")


@lru_cache(maxsize=1)
def get_audio_analysis_model():
    """Modelo Wav2Vec2 para análise acústica de emoções no som"""
    return pipeline("audio-classification", model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition")
