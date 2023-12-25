
import json
from pathlib import Path

from pydub import AudioSegment
from trainer import Trainer, TrainerArgs
from TTS.tts.configs.glow_tts_config import GlowTTSConfig
from TTS.tts.configs.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models.glow_tts import GlowTTS
from TTS.tts.utils.text.tokenizer import TTSTokenizer
from TTS.utils.audio import AudioProcessor

List = list
Dict = dict

OUTPUT_PATH = Path.home() / 'data/tts/scarlet_train_dir'
OUTPUT_PATH.mkdir(exist_ok=True)
(OUTPUT_PATH / 'wavs').mkdir(exist_ok=True)

# %%
# ideas:
#  - Morgan Freeman
#  - Ron Swanson
#  - David Attenborough
#  - PBS Physics Dude
#  - Sabine Hosenfelder
#  - Scarlet Johanson
# %%


def _transcribe():
    # %%
    import whisper
    model = whisper.load_model("medium")

    mp3_file = Path.home() / 'data/tts/audio/barackobamamlkremembrance.mp3'
    # speaker_name = "obama"
    # wav_file = Path(str(mp3_file).replace('.mp3', '.wav'))
    result = model.transcribe(str(mp3_file))
    # %%
    Path(str(mp3_file) + ".json").write_text(json.dumps(result, indent=4))
    # %%
    result = json.loads(Path(str(mp3_file) + ".json").read_text())
    # %%
    segments = result['segments']

    sound = AudioSegment.from_mp3(mp3_file)

    # %%


def _train():
    """This follows
    https://github.com/coqui-ai/TTS/blob/dev/notebooks/Tutorial_2_train_your_first_TTS_model.ipynb
    """
    # %%
    output_path = OUTPUT_PATH

    dataset_config = BaseDatasetConfig(
        formatter="ljspeech", meta_file_train="metadata.csv",
        path=str(output_path),
    )

    config = GlowTTSConfig(
        batch_size=32,
        eval_batch_size=16,
        eval_split_size=0.10,
        num_loader_workers=4,
        num_eval_loader_workers=4,
        run_eval=True,
        test_delay_epochs=-1,
        epochs=100,
        text_cleaner="phoneme_cleaners",
        use_phonemes=True,
        phoneme_language="en-us",
        phoneme_cache_path=str(output_path / "phoneme_cache"),
        print_step=25,
        print_eval=False,
        mixed_precision=True,
        output_path=str(output_path),
        datasets=[dataset_config],
        save_step=1000,
    )
    ap = AudioProcessor.init_from_config(config)
    ap.sample_rate = 22050

    tokenizer, config = TTSTokenizer.init_from_config(config)
    # %%
    train_samples, eval_samples = load_tts_samples(
        dataset_config,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )
    print('train_samples', len(train_samples))
    print( "".join( f"{Path(d['audio_file']).name} : {d['text']}" for d in train_samples[:5]) )
    print('eval_samples', len(eval_samples))
    # %%
    model = GlowTTS(config, ap, tokenizer, speaker_manager=None)

    trainer = Trainer(
        TrainerArgs(), config, output_path, model=model, train_samples=train_samples,
        eval_samples=eval_samples,
    )

    trainer.fit()
    # %%


def _make_metadata_csv(segments: List[Dict], speaker_name: str):
    # %%
    with Path(OUTPUT_PATH / 'metadata.csv').open("wt") as f_out:
        for i, segment in enumerate(segments):
            text = segment['text'].strip()
            print(f"audio_{i:04}|{speaker_name}|{text}", file=f_out)
    # %%


def _make_audio_clips(sound: AudioSegment, segments: List[Dict]):
    # %%
    for i, segm in enumerate(segments):
        start_ms = segm['start'] * 1000
        end_ms = segm['end'] * 1000
        clip = sound[start_ms:end_ms]
        clip_mono = clip.set_channels(1).set_frame_rate(22050)
        clip_mono.export(OUTPUT_PATH / f"wavs/audio_{i:04}.wav", format="wav")
        if i % 20 == 0:
            print(i)
    # %%
