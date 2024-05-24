import re
import json
import spacy
from multiprocessing import Pool
from tqdm import tqdm

from utils.fsys import read_lines
from utils.regexes import regex_match, compile
from utils.fsys import list_files, read_lines


def main(input_docs, output_file, cpu_count, tqdm_conf):
    texts = preprocess(list_files(input_docs), tqdm_conf, cpu_count)
    matches = process(Process(), texts, tqdm_conf, 12)
    with open(output_file, 'w') as s:
        json.dump(matches, s, ensure_ascii=False, indent=4)


def preprocess(input_files, tqdm_conf, cpu_count):
    fn = Preprocess()
    with Pool(cpu_count) as p:
        texts_list = tqdm(p.imap(fn, input_files), desc='preprocess', total=len(input_files), **tqdm_conf)
        texts_list = {f: t for f, t in list(texts_list)}
    return texts_list
        

def process(fn, spans, tqdm_conf, cpu_count):
    with Pool(cpu_count) as p:
        matches = list(tqdm(p.imap(fn, spans.items()), desc='process', total=len(spans), **tqdm_conf))
    return {f: t for f, t in matches}


class Preprocess:
    def __init__(self):
        Preprocess.regex = compile({
            'args': {'flags': re.MULTILINE},
            'expr': r'^[^А-ЯЁа-яёA-Za-z]*([А-ЯЁа-яёA-Za-z\d:;!? ,.\-\\\/(){}\[\]]+)',
            'groups': (1,),
        })
    
    @classmethod
    def __call__(cls, file):
        text = read_lines(file)
        matches = regex_match(Preprocess.regex, text)
        return file, [m['groups'][0] for m in matches]


class Process:
    def __init__(self):
        Process.nlp = spacy.load('ru_core_news_lg')

    @classmethod
    def __call__(cls, item):
        file, spans = item
        pers, locs = set(), set()

        for s in spans:
            doc = cls.nlp(s)
            for word in doc.ents:
                if word.label_ == 'PER':
                    pers.add(word.text)
                if word.label_ == 'LOC' \
                        or word.label_ == 'GPE':
                    locs.add(word.text)

        return file, {'pers': list(pers), 'locs': list(locs)}
