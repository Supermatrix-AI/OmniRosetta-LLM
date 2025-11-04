from PIL import Image
from TTS.api import TTS


tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")


def speak(text):
    tts.tts_to_file(text=text, file_path="output.wav")


def see(img_path):
    return Image.open(img_path).size
