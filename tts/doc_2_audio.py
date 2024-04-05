#!/bin/env python
"""Turn a long text into a sound file (wav or mp3), using Coqui TTS: text-to-speech

Example usages:

# Generate a wav file from a plain text document (assumed to be utf-8 encoded by default)
# Path to wav file will my_dir/my_document.wav
./doc_2_audio.py my_dir/my_document.txt

# Will produce output file: my_dir/my_document.wav

# Generate a wav file from a plain text document encoded in utf-16
# (all encodings supported by Python open() are supported here, e.g. cp1252, iso-8859-1, etc.)
./doc_2_audio.py -e utf-16 my_dir/my_document.txt

# Generate a wav file from a PDF document (requires PyPDF2 Python library to be installed)
./doc_2_audio.py  my_dir/my_document.pdf

# Generate a wav file from a PDF document and wrongly split/concatenated words
# (requires PyPDF2 and enchant Python libraries to be installed)
./doc_2_audio.py -c my_dir/my_document.pdf

# Generate an mp3 file from a PDF
# (requires PyPDF2 and pydub Python libraries)
./doc_2_audio.py -f mp3  my_dir/my_document.pdf

# Will produce output file: my_dir/my_document.mp3

For other options:
./doc_2_audio.py -h

Requirements:
pip install TTS  # install coqui-tts library for text to speech conversion
pip install PyPDF2  # only needed if input doc is going to be in PDF format
pip install pyenchant # only needed if passing --clean-words
pip install pydub # only needed if passing

It could be a good idea to create venv first (before pip install):
python3 -m venv venv-d2a; venv-d2a/bin/activate.sh; pip install wheel

Todo:
----
- Automatically extract plain text from a pdf document.
- Generate mp3 instead of wav

"""
from typing import Optional, Protocol

import enchant
import numpy as np
import argparse
from pathlib import Path

import re

import torch
from TTS.api import TTS
from TTS.utils.audio.numpy_transforms import save_wav

TTS_MODELS_BY_KEY = {
    'vits': 'tts_models/en/vctk/vits'
}
# %%


def main():

    args = get_cli_args()

    run(in_file=Path(args.in_file),
        encoding=args.encoding,
        tts_model_key=args.tts_model_key,
        speaker=args.speaker,
        clean_words=args.clean_words,
        out_fmt=args.out_fmt)


class WordChecker(Protocol):
    def check(self, word: str) -> bool:
        pass
# %%


def get_cli_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('in_file', help='input text or pdf file')
    arg_parser.add_argument('-e', '--encoding', help="input text file's encoding",
                            default="utf8")
    arg_parser.add_argument('-k', '--tts_model_key',
                            help=f'tts model key, possible values: '
                                 f'{list(TTS_MODELS_BY_KEY.keys())}',
                            default="vits")
    arg_parser.add_argument('-s', '--speaker',
                            help='speaker used in the case of a multi-speaker model',
                            default="p225")

    arg_parser.add_argument('-c', '--clean-words',
                            help='clean words in extracted text',
                            action='store_true')

    arg_parser.add_argument('-f', '--out-fmt',
                            help='the format of the output, either `mp3` or `wav`',
                            default='wav')

    return arg_parser.parse_args()


def run(*, in_file: Path, encoding: str, tts_model_key: str,
        speaker: str, clean_words: bool, out_fmt: str) -> None:
    # Get device
    tts_model_name = TTS_MODELS_BY_KEY[tts_model_key]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts_model = TTS(tts_model_name).to(device)

    in_txt_file = maybe_convert_to_txt(in_file, clean_words)
    if in_txt_file is None:
        return None

    sections = read_text_file(in_txt_file, encoding=encoding)
    # text = "\n".join(sections)

    out_wav_file = in_txt_file.with_suffix(".wav")
    tts_by_sections(tts_model, sections=sections, speaker=speaker, out_wav_path=out_wav_file)

    if out_fmt == 'mp3':
        produce_mp3_output(out_wav_file)
        out_wav_file.unlink()
    else:
        print(f"Done generating wav file: {out_wav_file}")


def maybe_convert_to_txt(in_file: Path, clean_words: bool) -> Optional[Path]:
    if in_file.suffix == '.pdf':
        in_txt_file = in_file.with_suffix('.txt')

        if not in_txt_file.exists():
            print(f'Extracting text from pdf and writing to .txt file: {in_txt_file.name}')
            txt = extract_text_from_pdf(in_file, clean_words)
            in_txt_file.write_text(txt, encoding="utf-8")
        else:
            print(f"Input file is pdf but txt version ({in_txt_file}) already exists, "
                  f"not overwriting, in case txt version has been editted manually")
        return in_txt_file
    elif in_file.suffix == '.txt':
        return in_file
    else:
        print(f"ERROR: Extension of input file is {in_file.suffix}, can't only handle "
              f"PDF and TXT")
        return None

# %%


def extract_text_from_pdf(pdf_path: Path, clean_words: bool) -> str:
    # %%
    extracted_text = ""
    import PyPDF2
    # %%
    try:
        extracted_texts = []
        with open(pdf_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                extracted_texts.append(page.extract_text())
    except FileNotFoundError:
        return "Error: File not found."
    # %%
    extracted_text = "\n".join(extracted_texts)

    lang = auto_detect_language(extracted_text)
    word_checker = enchant.Dict(lang) if clean_words else None
    # %%
    # sections = re.split("\n\n", whole_text, flags=re.MULTILINE)
    sections = reconcat_lines(extracted_text.split('\n'))

    print(f"{len(sections)} sections found:")

    clean_sections = []
    for i, section_raw in enumerate(sections):
        section = clean_section(section_raw, word_checker=word_checker)
        print(f"    {i:4d}. (len: {len(section):4d}): {section[:32]} ... {section[-32:]}")
        clean_sections.append(section)
    # %%

    return "\n".join(clean_sections)

# %%


def read_text_file(in_txt_file: Path, encoding: str = "utf8") -> list[str]:
    """Return one string for each section"""
    whole_text = in_txt_file.read_text(encoding=encoding)

    sections = whole_text.split('\n')
    return sections


def tts_by_sections(tts_model: TTS, *, speaker: str, sections: list[str], out_wav_path: Path):

    n_sections = len(sections)
    total_len = sum(len(section) for section in sections)
    processed_len = 0
    wavs: list[np.ndarray] = []

    sections_ = [section for section in sections if len(section) > 0]
    if len(sections_) < len(sections):
        print(f'Discarded {len(sections) - len(sections_)} empty sections.')
    del sections

    for i, section in enumerate(sections_):
        wav_list = tts_model.tts(text=section, speaker=speaker)
        processed_len += len(section)

        wav = np.array(wav_list)
        print(f"Done with section {i:4d} / {n_sections}, progress: "
              f"{processed_len / total_len * 100:3.1f} % \n")
        wavs.append(wav)
        # TODO: add pause between consecutive wavs ?

    final_wav = np.hstack(wavs)
    final_len_secs: float = len(final_wav) / tts_model.synthesizer.output_sample_rate
    print(f'Saving final wav with {len(final_wav)} samples '
          f'({final_len_secs:.2f} s) to: {out_wav_path}')
    save_wav(wav=final_wav, path=str(out_wav_path),
             sample_rate=tts_model.synthesizer.output_sample_rate)

# %%


def reconcat_lines(lines: list[str]) -> list[str]:
    """Process lines so that a line ending in '-'
    is concatted to the next line (if starting with a lowercase letter)"""
    out_lines = []
    curr_line = ''

    for line in lines:
        if curr_line.endswith('-') and line[0].lower() == line[0]:
            curr_line = curr_line[:-1] + line
        elif len(line) > 0 and line[0].lower() == line[0]:
            curr_line += ' ' + line
        else:
            if curr_line != '':
                out_lines.append(curr_line)
            curr_line = line

    out_lines.append(curr_line)

    return out_lines
# %%


def clean_section(section_raw: str, word_checker: Optional[WordChecker]) -> str:
    # %%
    lines = section_raw.split("\n")
    new_lines = [clean_line(line, word_checker) for line in lines]
    # %%
    return " ".join(new_lines)
# %%


def clean_line(line: str, word_checker: Optional[WordChecker]) -> str:
    # %%
    clean_line = line.replace('ﬁ', 'fi').strip()
    if word_checker is None:
        return clean_line
    else:
        words = clean_line.split()
        return " ".join(clean_word(word, word_checker) for word in words)
# %%


def clean_word(word: str, word_checker: WordChecker) -> str:
    if len(word) == 0:
        return word

    if word[-1] in ',;?.)(!':
        return clean_word(word[:-1], word_checker) + word[-1]

    if '-' in word:
        no_dash = word.replace('-', '')
        if word_checker.check(no_dash):
            # print(f'removed dash: `{word}` -> {no_dash}')
            return no_dash
        else:
            return word
    else:
        if word_checker.check(word):
            return word
        else:

            # print(f'Word: `{word} not in dict.', end=' ')
            for i in range(1, len(word) - 1):
                part1 = word[:i]
                part2 = word[i:]

                if word_checker.check(part1) and word_checker.check(part2):
                    # print(f'split word: {part1} {part2}')
                    return f'{part1} {part2}'

            return word
# %%


def auto_detect_language(text: str, candidate_langs: list[str] = None) -> str:
    words = [w for w in re.split(r'\W', text) if len(w) > 0]

    def score_lang(lang: str) -> float:
        lang_dict = enchant.Dict(lang)
        n_words_in_dict = sum(lang_dict.check(word)
                              for word in words if lang_dict.check(word))
        score = -n_words_in_dict / len(words) * 100.0
        print(f"score for {lang}: {score:.2f}")

        return score

    if candidate_langs is None:
        candidate_langs = ['en', 'es']

    assert len(candidate_langs) > 0
    langs_by_score = sorted(candidate_langs, key=score_lang)

    return langs_by_score[0]
# %%


def produce_mp3_output(out_wav_file: Path):
    from pydub import AudioSegment

    audio = AudioSegment.from_wav(out_wav_file)
    out_mp3_file = out_wav_file.with_suffix('.mp3')
    audio.export(out_mp3_file, format='mp3')
    print(f"Done generating mp3 file: {out_mp3_file}")


def interactive_testing():
    # %%
    runfile("tts/doc_2_audio.py")

    # %%
    pdf_path = Path("/home/teo/gdrive_rclone/Academico/MAIA/Etica de la IA/Week 1/"
                    "1.7-Why-Teaching-ethics-to-AI-practitioners-is-important.pdf")
    # %%
    pdf_text = extract_text_from_pdf(pdf_path, clean_words=True)
    print(pdf_text[:10])
    # Print the extracted text
    # %%
    lines = read_text_file(pdf_path.with_suffix('.txt'))
    # text = pdf_path.with_suffix('.txt').read_text(encoding='utf-8')

    for i, line in enumerate(lines):
        print(f"{i:5d} | {line}")

    # %%
    sections = reconcat_lines(lines)

    for i, line in enumerate(sections):
        print(f"{i:5d} | {line}")

    # %%
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts_model = TTS('tts_models/en/vctk/vits').to(device)
    # wav = tts.tts(sections[35], speaker='p225')
    # %%
    tts_by_sections(tts_model, speaker='p225', sections=sections[0: 10],
                    out_wav_path=Path('./test.wav'))
    # %%
    import enchant

    word_checker = enchant.Dict('en')

    result = clean_word('fr-om', word_checker=word_checker)
    print(result)
    # %%


if __name__ == '__main__':
    main()
