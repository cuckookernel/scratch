
import tempfile
import time
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyaudio
import whisper
from numpy.linalg import norm
from whisper.audio import SAMPLE_RATE

Array = np.ndarray


@dataclass
class AudioParams:
    frames_per_chunk: int = 1024  # Record in chunks of 1024 samples
    sample_format: int = pyaudio.paInt16  # 16 bits per sample
    channels: int = 2
    frames_per_second: int = SAMPLE_RATE


@dataclass
class Recording:
    data: bytes
    sample_width: int
    params: AudioParams
# %%


def _main():
    # %%
    whisper_model = whisper.load_model("small")
    # %%
    max_seconds = 3.0
    params = AudioParams()

    recording = record_audio(params, max_seconds)

    transcription = transcribe(whisper_model, recording)
    print(transcription['text'])
    # %%


def record_audio(params: AudioParams, max_seconds: float) -> Recording:
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    stream = p.open(format=params.sample_format, channels=params.channels,
                    rate=params.frames_per_second, frames_per_buffer=params.frames_per_chunk,
                    input=True)

    chunks = []  # Initialize array to store frames
    # arrays = []
    # Store data in chunks for 3 seconds
    max_chunks = max_seconds * params.frames_per_second / params.frames_per_chunk
    print(f"Recording (max_seconds={max_seconds}) ...")
    while len(chunks) < max_chunks:
        chunk = stream.read(params.frames_per_chunk)
        chunks.append(chunk)
        arr = np.frombuffer(chunk, '<i2')
        # arrays.append(arr)
        print(f"len(chunks) = {len(chunks)} avg_power({np.log(avg_power(arr))})        \r", end='')
        # Stop and close the stream
    p.terminate()
    print('Finished recording')

    return Recording(data=b''.join(chunks), params=params,
                     sample_width=p.get_sample_size(params.sample_format))
# %%


def transcribe(whisper_model, rec: Recording):
    t0 = time.perf_counter()
    tmp_fpath = tempfile.mktemp(suffix=".wav")
    with wave.open(tmp_fpath, 'wb') as wf:
        wf.setsampwidth(rec.sample_width)
        wf.setnchannels(rec.params.channels)
        wf.setframerate(rec.params.frames_per_second)
        wf.writeframes(rec.data)
    t1 = time.perf_counter()
    print(f'saving wave file: {t1 - t0:.3f}s')
    transcription = whisper_model.transcribe(tmp_fpath)

    Path(tmp_fpath).unlink()
    t2 = time.perf_counter()
    print(f'transcribing: {t2 - t1:.3f}s')

    return transcription


def avg_power(arr: Array) -> float:
    return norm(arr, 2) ** 2 / len(arr)
    # %%
