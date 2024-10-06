import re
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, \
    NewsSyntaxParser, NewsNERTagger, PER, LOC, NamesExtractor, AddrExtractor, Doc

from utils.fsys import read_lines
from utils.regexes import compile
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
    return [r for m in matches for r in m]


class Preprocess:
    @classmethod
    def __call__(cls, file):
        return file, read_lines(file).split('\n')


class Process:
    def __init__(self):
        Process.segmenter = Segmenter()
        Process.morph_vocab = MorphVocab()
        Process.emb = NewsEmbedding()
        Process.morph_tagger = NewsMorphTagger(Process.emb)
        Process.syntax_parser = NewsSyntaxParser(Process.emb)
        Process.ner_tagger = NewsNERTagger(Process.emb)
        Process.names_extractor = NamesExtractor(Process.morph_vocab)
        Process.addr_extractor = AddrExtractor(Process.morph_vocab)

    @classmethod
    def __call__(cls, item):
        file, spans = item
        output = []

        for s in spans:
            d = Doc(s)
            d.segment(cls.segmenter) 
            d.tag_morph(cls.morph_tagger)
            d.parse_syntax(cls.syntax_parser)
            d.tag_ner(cls.ner_tagger)

            for span in d.spans:
                span.normalize(cls.morph_vocab)
                if span.type == PER:
                    span.extract_fact(cls.names_extractor)
                if span.type == LOC:
                    span.extract_fact(cls.addr_extractor)
                
            output.extend((file, 'natasha', 'per', _.text) for _ in d.spans if _.fact and _.type == PER)
            output.extend((file, 'natasha', 'loc', _.text) for _ in d.spans if _.fact and _.type == LOC)

        return output
    