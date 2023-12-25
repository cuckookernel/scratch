use std::collections::HashSet;
use std::io::{self, BufRead};
use std::fs::File;
use std::path::Path;

const WORDS_FILE : &str = "/home/teo/Downloads/bip39-english.txt";
const TARGET_LEN: usize = 12;


struct Recognizer {
    words: HashSet<String>,
    recognized: Vec<String>,
    unrecognized_cnt : usize,  // count of consecutive un recognized
    max_unrecognized_cnt: usize, // = 1 max_unrecognized_cnt
    max_recog_len: usize,
    _debug_matched_words: i32, //
}

struct Match {
    words: Vec<String>
}


impl Default for Recognizer {
    fn default() -> Self {
        Self {
            words: HashSet::new(),
            recognized: Vec::new(),
            unrecognized_cnt: 0,
            max_unrecognized_cnt: 1,
            max_recog_len: 0,
            _debug_matched_words: 0
        }
    }
}


impl Recognizer {

    fn check_match(&mut self) -> Option<Match> {
        self.max_recog_len = self.max_recog_len.max(self.recognized.len());

        if self.recognized.len() >= TARGET_LEN {
            Some(Match{words: self.recognized.clone()})
        }
        else {
            None
        }
    }

    fn reset(& mut self){
        self.recognized.clear();
        self.unrecognized_cnt = 0
    }

    fn push(&mut self, word: &str) -> Option<Match> {
        if self.words.contains(word) {
            self.recognized.push(word.to_owned());
            //# print(self.recognized)
            self._debug_matched_words += 1;
            self.unrecognized_cnt = 0
        }
        else {
            self.unrecognized_cnt += 1
        }

        let mut match_ = self.check_match();

        // only emit match if reset happen
        if self.unrecognized_cnt >= self.max_unrecognized_cnt {
            self.reset()
        } else {
            match_ = None
        }
        // print( str(self) )

        return match_
    }
    /*
    def __str__(self):
        return f"recognized: {self.recognized} unr_count: {self.unrecognized_cnt} " \
               f"max_recog_len({self.max_recog_len}) dbg_match_words({self._debug_matched_words})"

    */
}

fn make_recognizer() -> Recognizer {
    let read_res = read_lines(WORDS_FILE);

    let lines = read_res.unwrap();

    let mut words = HashSet::new();

    for maybe_line in lines {
        if let Ok(line0) = maybe_line {
            let line = line0.strip_suffix("\n").unwrap_or(&line0);
            words.insert(line.to_owned());
        }
    }

    Recognizer {words, .. Default::default()}
}


fn main() {

    let mut recog = make_recognizer();

    eprintln!("Recognizer has: {}", recog.words.len());

    let crawl_file = "/home/teo/Downloads/CC-MAIN-20221007210452-20221008000452-00773.warc.wet";

    let mut lines_cnt = 0;
    let mut words_cnt = 0;


    let lines = read_lines(crawl_file).unwrap();
    for line_res in lines {
        if let Ok(line) = line_res {
            lines_cnt += 1;
            let words = line.split(&['\t', ' ', '\n'][..]).collect();
            // let words: Vec<&str> = line.split(&['\t', ' ', '\n'][..]).collect();
            // words_cnt += words.len();

            for word in words {
                let maybe_match = recog.push(word);
                if let Some(match_) = maybe_match {
                    println!( "{:?}", match_.words );
                }
            }

            if lines_cnt % 50000 == 0 {
                eprint!("{} {} {} {} \r", lines_cnt, words_cnt, recog.max_recog_len, recog._debug_matched_words)
            }
        }

    }

}

// The output is wrapped in a Result to allow matching on errors
// Returns an Iterator to the Reader of the lines of the file.
fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where P: AsRef<Path>, {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}
