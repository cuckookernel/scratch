
import wave

import pyaudio

List = list
FRAME_RATE = 44100
FORMAT = pyaudio.paInt16
# %%


def _main():
    # %%
    p = pyaudio.PyAudio()
    # %%
    stream = p.open(format=FORMAT,
                    channels=1,
                    rate=FRAME_RATE, input=True,
                    frames_per_buffer=1024)

    frames = []
    # %%
    try:
        while True:
            data = stream.read(1024)
            frames.append(data)
    except KeyboardInterrupt:
        print(f"frames has: {len(frames)}")

    # %%
    sample_width = p.get_sample_size(FORMAT)
    # %%


def save_file(frames: List[bytes], sample_width: int):
    # %%
    with wave.open("output.wav", "wb") as out_f:
        out_f.setnchannels(1)
        out_f.setsampwidth(sample_width)
        out_f.setframerate(FRAME_RATE)
        out_f.writeframes(b''.join(frames))
    # %%
