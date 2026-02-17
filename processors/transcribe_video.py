from moviepy import VideoFileClip
import speech_recognition as sr


def extract_audio_from_video(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)


def transcribe_audio_to_text(audio_path, text_output_path):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio, language="en-US")
            print("Transcrição: " + text)

            with open(text_output_path, 'w', encoding='utf-8') as file:
                file.write(text)

            return text

        except sr.UnknownValueError:
            print("Google Speech Recognition não conseguiu entender o áudio")
            return ""
        except sr.RequestError as e:
            print(
                "Erro ao solicitar resultados do serviço de reconhecimento de fala do Google; {0}".format(e))
            return ""
