#!/bin/env python
"""
Turn a long text into a sound file, using Coqui TTS: text-to-speech

"""

import re
import argparse
from pathlib import Path

import torch
from TTS.api import TTS

TTS_MODELS_BY_KEY = {
    'vits': 'tts_models/en/vctk/vits'
}
# %%


def main():

    args = get_cli_args()

    run(in_txt_file=Path(args.in_txt_file),
        encoding=args.encoding,
        tts_model_key=args.tts_model_key,
        speaker=args.speaker)


def get_cli_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('in_txt_file', help='input text file')
    arg_parser.add_argument('-e', '--encoding', help="input text file's encoding",
                            default="utf8")
    arg_parser.add_argument('-k', '--tts_model_key',
                            help=f'tts model key, possible values: '
                                 f'{list(TTS_MODELS_BY_KEY.keys())}',
                            default="vits")
    arg_parser.add_argument('-s', '--speaker',
                            help=f'speaker used in the case of a multispeaker model',
                            default="p225")

    return arg_parser.parse_args()


def run(*, in_txt_file: Path, encoding: str, tts_model_key: str,
        speaker: str) -> None:
    # Get device
    tts_model_name = TTS_MODELS_BY_KEY[tts_model_key]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS(tts_model_name).to(device)

    sections = read_text_file(in_txt_file, encoding=encoding)
    text = "\n".join(sections)

    out_wav_file = in_txt_file.with_suffix(".wav")
    tts.tts_to_file(text=text, speaker=speaker, file_path=out_wav_file)
    print(f"Done generating wav file: {out_wav_file}")

    # %%


def read_text_file(in_txt_file: Path, encoding) -> list[str]:
    """Return one string for each section"""
    whole_text = in_txt_file.read_text(encoding=encoding)
    sections = re.split("\n\n", whole_text, flags=re.MULTILINE)

    print(f"{len(sections)} sections found:")
    for i, section_raw in enumerate(sections):
        section = clean_section(section_raw)
        print(f"    {i}: {len(section)} :  {section[:16]} .. {section[-16:]}")

    return sections
# %%


def clean_section(section: str) -> str:
    lines = section.split("\n")
    new_lines = [line.strip().strip('"') for line in lines]
    return " ".join(new_lines)
    # %%


def _interactive_testing():
    # %%
    in_txt_file = Path("/home/teo/gdrive_rclone/EBooks/Machine Learning & Statistics/"
                       "Incorporating_Ethics_into_Artificial_Intelligence_.txt")
    encoding = "utf8"

    run(in_txt_file=in_txt_file, encoding=encoding,
        tts_model_key="vits", speaker="p225")
    # %%


if __name__ == '__main__':
    main()
