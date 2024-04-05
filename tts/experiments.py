# %%
# Robotic voice
import pyttsx3

engine = pyttsx3.init()
engine.say("I will speak this text")
engine.runAndWait()
# %%
# Using coqui-tts

import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Init TTS
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
tts = TTS("tts_models/en/vctk/vits").to(device)

text = """
The text explores the autonomy of smart machines, particularly in the context of driverless cars. Some scholars question the autonomy of human beings, citing causal determinism as a limiting factor for assigning moral responsibility. While acknowledging human free will, the author suggests that machines, despite their apparent smart decision-making, may not truly act autonomously. The concept of autonomy is viewed as a continuum, with tools like hammers having no autonomy, basic GPS systems possessing limited autonomy based on predefined algorithms, and advanced AI-equipped machines demonstrating higher autonomy by making decisions in response to various guidelines and real-time information.
"""

tts.tts_to_file(text=text, speaker="p225",
                file_path="/home/teo/vits-summary-p225.mp3")
# %%
""""
 1: tts_models/multilingual/multi-dataset/xtts_v2 [already downloaded]
 3: tts_models/multilingual/multi-dataset/your_tts [already downloaded]
 11: tts_models/en/ljspeech/tacotron2-DDC [already downloaded]
 13: tts_models/en/ljspeech/glow-tts [already downloaded]
 14: tts_models/en/ljspeech/speedy-speech [already downloaded]
 15: tts_models/en/ljspeech/tacotron2-DCA [already downloaded]
 16: tts_models/en/ljspeech/vits [already downloaded]
 21: tts_models/en/vctk/vits [already downloaded]
 28: tts_models/es/mai/tacotron2-DDC [already downloaded]
 29: tts_models/es/css10/vits [already downloaded]
 2: vocoder_models/universal/libri-tts/fullband-melgan [already downloaded]
 4: vocoder_models/en/ljspeech/multiband-melgan [already downloaded]
 5: vocoder_models/en/ljspeech/hifigan_v2 [already downloaded]
"""

# %%
# Run TTS
# ❗ Since this model is multi-lingual voice cloning model,
# we must set the target speaker_wav and language
# Text to speech list of amplitude values as output
wav = tts.tts(text="Hello world!", speaker_wav="my/cloning/audio.wav", language="en")
# Text to speech to a file
tts.tts_to_file(text="Hello world!", speaker_wav="my/cloning/audio.wav", language="en",
                file_path="output.wav")
