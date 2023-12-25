from pathlib import Path
from typing import Set

# "https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt"
words_file = Path("/home/teo/Downloads/bip39-english.txt")

crawl_file = Path("/home/teo/Downloads/CC-MAIN-20221007210452-20221008000452-00773.warc.wet")



def _main():
    # %%
    words = { line.strip() for line in words_file.read_text().split("\n") }
    recog = Recognizer(words, max_unrecognized_cnt=1)
    # %%
    recog.push("grunt")
    # %%

    run_one_file(recog, crawl_file)
    # %%



class Recognizer:
    def __init__(self, words: Set[str], max_unrecognized_cnt: int = 3):
        self.words = words
        self.recognized = []
        self.unrecognized_cnt = 0  # count of consecutive un recognized
        self.max_unrecognized_cnt = max_unrecognized_cnt
        self.max_recog_len = 0
        self._debug_matched_words = 0

    def check_match(self):
        self.max_recog_len = max(self.max_recog_len, len(self.recognized))

        if len(self.recognized) >= 12:
            return self.recognized.copy()
        else:
            return None

    def reset(self):
        self.recognized.clear()
        self.unrecognized_cnt = 0

    def push(self, word: str) -> bool:
        if word in self.words:
            self.recognized.append(word)
            # print(self.recognized)
            self._debug_matched_words += 1
            self.unrecognized_cnt = 0
        else:
            self.unrecognized_cnt += 1

        match = self.check_match()

        # only emit match if reset happens
        if self.unrecognized_cnt >= self.max_unrecognized_cnt:
            self.reset()
        else:
            match = None

        # print( str(self) )

        return match

    def __str__(self):
        return f"recognized: {self.recognized} unr_count: {self.unrecognized_cnt} " \
               f"max_recog_len({self.max_recog_len}) dbg_match_words({self._debug_matched_words})"

# %%


def run_one_file(recog: Recognizer, crawl_file: Path):

    lines_cnt = 0
    words_cnt = 0

    with crawl_file.open("rt") as f_in:
        for line in f_in.readlines():
            lines_cnt += 1
            words = line.split()
            words_cnt += len(words)

            for word in words:
                maybe_match = recog.push(word)
                if maybe_match:
                    print( maybe_match )

            if lines_cnt % 50000 == 0:
                print(lines_cnt, words_cnt, recog.max_recog_len, recog._debug_matched_words,
                      end="\r")

    # %%

if __name__ == "__main__":
    _main()
