# coding=utf-8
import re

def load_vocabulary(words_file):
    return set([X.split(' ')[0] for X in open(words_file).read().split('\n')])

def kaldi_normalize(txt, vocab):
    # lowercase
    norm = txt.lower()
    # Turn fancy apostrophes into simpler apostrophes
    norm = norm.replace("’", "'")
    # preserve in-vocab hyphenated phrases
    if norm in vocab:
        return [norm]
    # turn hyphens into spaces
    norm = norm.replace('-', ' ')
    # remove all punctuation
    norm = re.sub(r'[^a-z0-9\s\']', ' ', norm)
    seq = norm.split()
    # filter out empty words
    seq = [x.strip() for x in seq if len(x.strip())>0]
    # replace [oov] words
    seq = [x if x in vocab else '[oov]' for x in seq]

    return seq

class MetaSentence:
    """Maintain two parallel representations of a sentence: one for
    Kaldi's benefit, and the other in human-legible form.
    """

    def __init__(self, sentence, vocab):
        self.raw_sentence = sentence
        self.vocab = vocab

        self._gen_kaldi_seq(sentence)

    def _gen_kaldi_seq(self, sentence):
        self._seq = []
        for m in re.finditer(r'[^ \n]+', sentence):
            start, end = m.span()
            word = m.group()
            if len(word.strip()) == 0:
                continue
            token = kaldi_normalize(word, self.vocab)
            self._seq.append({
                "start": start,
                "end": end,
                "token": token,
            })

    def get_kaldi_sequence(self):
        return reduce(lambda acc,y: acc+y["token"], self._seq, [])

    def get_matched_kaldi_sequence(self):
        return ['-'.join(X["token"]) for X in self._seq]

    def get_display_sequence(self):
        display_sequence = []
        for x in self._seq:
            start, end = x["start"], x["end"]
            word = self.raw_sentence[start:end]
            display_sequence.append(word)
        return display_sequence

    def get_text_offsets(self):
        return [(x["start"], x["end"]) for x in self._seq]
