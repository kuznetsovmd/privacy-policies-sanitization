from collections import Counter
import json
from multiprocessing import Pool
from tqdm import tqdm
from utils.fsys import read_lines
from utils.regexes import regex_match, compile
from nltk.corpus import stopwords
import nltk
from pymystem3 import Mystem


def frequent(input_files, tqdm_conf, stopwords_list, cpu_count, words_cnt):
    nltk.download("stopwords")

    russian_stopwords = stopwords.words('russian')
    russian_stopwords.extend(stopwords_list)

    fn = GenFrequent(russian_stopwords)
    with Pool(cpu_count) as p:
        texts_list = tqdm(p.imap(fn, input_files), desc='get-frequent', total=len(input_files), **tqdm_conf)
        texts_list = {f: t for f, t in list(texts_list)}

    flatten = [w for t in texts_list.values() for w in t]
    frequent_words = {k: v for k, v in sorted(Counter(flatten).items(), key=lambda x: -x[1])[:words_cnt]} # word_cnt = 50 ; choose words ; count words in docs and plot

    filtered = []
    for f, t in tqdm(texts_list.items(), desc='frequent', **tqdm_conf):
        if not any(w in t for w in frequent_words):
            filtered.append(f)
    return frequent_words, filtered


class GenFrequent:
    def __init__(self, stopwords):
        GenFrequent.stopwords = stopwords
        GenFrequent.lemmatizer = Mystem()
        GenFrequent.regex = compile({
            'args': {},
            'expr': r'[А-ЯЁа-яё]{3,}',
            'groups': (0,),
        })
    
    @classmethod
    def __call__(cls, file):
        text = read_lines(file)
        matches = regex_match(GenFrequent.regex, text)
        lemmatized = [cls.lemmatizer.lemmatize(m['groups'][0].lower())[0] for m in matches]
        return file, [l for l in lemmatized if l not in cls.stopwords]
    