import spacy
from multiprocessing import Pool
from tqdm import tqdm
import pandas as pd

from utils.fsys import read_lines
from utils.fsys import list_files, read_lines


def main(input_docs, output_file, cpu_count, tqdm_conf):
    texts = preprocess(list_files(input_docs), tqdm_conf, cpu_count)
    matches = process(Process(), texts, tqdm_conf, 12)
    df = pd.DataFrame(matches, columns=['file', 'library', 'type', 'value'])
    df.to_csv(output_file)


def preprocess(input_files, tqdm_conf, cpu_count):
    fn = Preprocess()
    with Pool(cpu_count) as p:
        texts_list = tqdm(p.imap(fn, input_files), desc='preprocess', total=len(input_files), **tqdm_conf)
        texts_list = {f: t for f, t in list(texts_list)}
    return texts_list
        

def process(fn, spans, tqdm_conf, cpu_count):
    with Pool(cpu_count) as p:
        matches = list(tqdm(p.imap(fn, spans.items()), desc='process', total=len(spans), **tqdm_conf))
    print(matches)
    return [r for m in matches for r in m]


class Preprocess:
    @classmethod
    def __call__(cls, file):
        return file, read_lines(file).split('\n')


class Process:
    def __init__(self):
        Process.nlp = spacy.load('ru_core_news_lg')

    @classmethod
    def __call__(cls, item):
        file, spans = item
        output = []

        for s in spans:
            doc = cls.nlp(s)
            for word in doc.ents:
                if word.label_ == 'PER':
                    output.append((file, 'spacy', 'per', word.text))
                if word.label_ == 'LOC' \
                        or word.label_ == 'GPE':
                    output.append((file, 'spacy', 'loc', word.text))

        return output
