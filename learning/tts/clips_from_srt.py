import re
from dataclasses import dataclass
from pathlib import Path

import bs4
import pandas as pd
from pydub.audio_segment import AudioSegment

DF = pd.DataFrame
Dict = dict
Record = Dict[str, str]

SRT_FILE = "/home/teo/Downloads/Her (2013) [1080p]/Her.scarlett-partial.srt"
MP3_FILE = "/home/teo/Downloads/Her (2013) [1080p]/Her-qa0-map-a.mp3"
OUTPUT_PATH = Path("/home/teo/data/tts/scarlet_train_dir/wavs")

# %%


def _main():
    # %%
    runfile("learning/tts/clips_from_srt.py")

    srt_text = Path(SRT_FILE).read_text().replace('\ufeff', '')

    pieces_df = process_srt_text(srt_text)
    print( pieces_df.head )
    # text = pieces_df['text'].iloc[0]
    pieces_df['text'] = (pieces_df['text'].str.replace('[\n ]+', ' ', regex=True)
                         .apply(lambda a_str: re.sub('SAMANTHA.*:[ \n]?', '', a_str)))
    # %%
    sound = AudioSegment.from_mp3(MP3_FILE)
    print(f"sound from: {MP3_FILE}, duration: {sound.duration_seconds:.3f} s")
    # %%


def process_srt_text(srt_text: str) -> DF:
    # %%
    pieces = re.split('\n{2,}', srt_text)

    # piece = pieces[0]

    for piece in pieces:
        if piece == '':
            continue
        parse_srt_piece(piece)
    srt_pieces = [parse_srt_piece(piece) for piece in pieces if piece != '']

    df = pd.DataFrame(srt_pieces)
    # %%
    return df


@dataclass
class SrtPiece:
    idx: int
    start_secs: float
    end_secs: float
    text: str
    text_raw: str


def parse_srt_piece(piece: str) -> SrtPiece:
    lines = piece.split('\n')
    idx = int(lines[0])
    tm_span = re.split(' --> ', lines[1])
    assert len(tm_span) == 2

    start_secs = time_offset_string_to_sec(tm_span[0])
    end_secs = time_offset_string_to_sec(tm_span[1])

    text_raw = "\n".join(lines[2:])
    soup = bs4.BeautifulSoup(text_raw, features='html.parser')

    return SrtPiece(idx=idx, start_secs=start_secs, end_secs=end_secs,
                    text_raw=text_raw, text=soup.get_text())
    # %%


# %%
def time_offset_string_to_sec(tm_offset_str: str) -> float:
    parts = tm_offset_str.split(',')
    secs_parts = parts[0].split(':')
    hrs, mins, secs = int(secs_parts[0]), int(secs_parts[1]), int(secs_parts[2])

    sec_fraction = float(parts[1]) / 1000.0
    total_secs = hrs * 3600.0 + mins * 60.0 + secs + sec_fraction
    return total_secs
# %%


def _make_audio_clips(sound: AudioSegment, pieces_df: DF):
    # %%
    recs = []
    print(f"saving clips to: {OUTPUT_PATH}")

    for i, piece in pieces_df.iterrows():
        start_ms = piece.start_secs * 1000
        end_ms = piece.end_secs * 1000
        clip = sound[start_ms:end_ms]
        clip_mono = clip.set_channels(1).set_frame_rate(22050)
        file_name = f"audio_{piece.idx:04}"
        recs.append({"file_name": file_name, "text": piece.text})
        clip_mono.export(OUTPUT_PATH / (file_name + ".wav"), format="wav")
        if int(i) % 20 == 0:
            print(i)
    # %%
    csv_path = OUTPUT_PATH / '../metadata.csv'
    print(f"saving metadata csv to {csv_path}")
    with csv_path.open("wt") as f_out:
        for rec in recs:
            print(f"{rec['file_name']}||{rec['text']}", file=f_out)
    # %%
