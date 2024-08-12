import json
import os
import re
import time

from collections import Counter
from tqdm import tqdm
from hashlib import md5
from multiprocessing import Pool
from pymystem3 import Mystem
from utils.regexes import regex_match, compile

from html_sanitization.sanitize import Sanitize
from utils.fsys import list_files, read_lines
from utils.timing import time_since


def gen_frequent(input_files, stopwords, cpu_count, words_cnt, 
        frequent_file, grams_n, tqdm_conf, **kwargs):
    files = list_files(input_files)

    fn = Preprocess(stopwords, grams_n)
    len_files = len(files)
    with Pool(cpu_count) as p:
        file_words = tqdm(p.imap(fn, files), desc='gen-frequent', total=len_files, **tqdm_conf)
        file_words = {f: t for f, t in list(file_words)}

    flatten = [w for t in file_words.values() for w in t]
    frequent_words = {k: v for k, v in sorted(Counter(flatten).items(), key=lambda x: -x[1])[:words_cnt]}
    
    s = sum(v for v in frequent_words.values())
    for k, v in frequent_words.items():
        frequent_words[k] = v / len_files

    with open(frequent_file, 'w') as s:
        json.dump(frequent_words, s, indent=4, ensure_ascii=False)


def main(input_files, stats_file, legacy_stats_file, frequent_words, cpu_count, sanitizer_conf, 
        deprecated_rules, sanitized_files, uppercase_threshold, short_threshold, 
        foreign_threshold, frequent_threshold, stopwords, grams_n, tqdm_conf, **kwargs):
    start = time.time()

    files = set(list_files(input_files))
    files, stats_deprecated = deprecated(files, deprecated_rules, tqdm_conf)
    files, stats_sanitize = sanitize(files, sanitized_files, sanitizer_conf, cpu_count, tqdm_conf)
    files, stats_short = short(files, short_threshold, tqdm_conf)
    files, stats_duplicates = duplicates(files, tqdm_conf)
    files, stats_uppercase = uppercase(files, uppercase_threshold, tqdm_conf)
    files, stats_foreign = foreign(files, foreign_threshold, tqdm_conf)
    files, stats_frequent = frequent(files, stopwords, cpu_count, frequent_words, frequent_threshold, grams_n, tqdm_conf)
    
    for f in set(list_files(f'{sanitized_files}/*.*')).difference(files):
        os.remove(f)

    statistics = {
        'total_input_docs': {
            'len': len(input_files)
        },
        **stats_deprecated,
        **stats_sanitize,
        **stats_short,
        **stats_duplicates,
        **stats_uppercase,
        **stats_foreign,
        **stats_frequent,
        'total_output_docs': {
            'cpu_count': cpu_count,
            'len': len(files),
            'total_time': time_since(start),
    }}

    with open(stats_file, 'w') as s:
        json.dump(statistics, s, ensure_ascii=False, indent=4)


def deprecated(input_files, deprecated_rules, tqdm_conf):
    now = time.time()

    filtered = set()
    for f in tqdm(input_files, desc='deprecated', **tqdm_conf):
        if not any(rule(f) for rule in deprecated_rules):
            filtered.add(f)

    return filtered, {
        'deprecated': {
            'len': len(filtered),
            'time': time_since(now),
    }}


def sanitize(input_files, sanitized_files, sanitizer_conf, cpu_count, tqdm_conf):
    now = time.time()

    fn = Sanitize(sanitized_files, **sanitizer_conf)
    with Pool(cpu_count) as p:
        output = list(tqdm(p.imap(fn, input_files), desc='sanitize', total=len(input_files), **tqdm_conf))

    stats = {f: s for f, s in output}
    return set(stats.keys()), {
        'sanitize': {
            'len': len(stats),
            'time': time_since(now),
            'stats': stats
    }}


def short(input_files, short_threshold, tqdm_conf): 
    now = time.time()

    stats = {}
    for f in tqdm(input_files, desc='short', **tqdm_conf):
        stats[f] = len(read_lines(f))
            
    stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[1])}
    filtered = dict(filter(lambda s: s[1] > short_threshold, stats.items()))
    return set(filtered.keys()), {
        'short': {
            'short_threshold': short_threshold,
            'len': len(stats),
            'time': time_since(now),
            'stats': stats
    }}


def duplicates(input_files, tqdm_conf):
    now = time.time()

    unique = {}
    for f in tqdm(input_files, desc='duplicates', **tqdm_conf):
        content = read_lines(f)
        hash = md5(content.encode('utf-8')).hexdigest()
        unique[hash] = f

    return set(unique.values()), {
        'duplicates': {
            'len': len(unique),
            'time': time_since(now)
    }}


def uppercase(input_files, uppercase_threshold, tqdm_conf):
    now = time.time()

    stats = {}
    for f in tqdm(input_files, desc='uppercase', **tqdm_conf):
        content = read_lines(f)
        upper = sum(1 for c in content if c.isupper())
        lower = sum(1 for c in content if c.islower())
        stats[f] = upper / (upper + lower)

    stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[1])}
    filtered = dict(filter(lambda s: s[1] < uppercase_threshold, stats.items()))
    return set(filtered.keys()), {
        'uppercase': {
            'uppercase_threshold': uppercase_threshold,
            'len': len(filtered),
            'time': time_since(now),
            'stats': stats
    }}


def foreign(input_files, foreign_threshold, tqdm_conf):
    now = time.time()

    stats = {}
    for f in tqdm(input_files, desc='foreign', **tqdm_conf):
        content = read_lines(f)
        russian = len(re.findall(r'[А-ЯЁа-яё]', content))
        foreign = len(re.findall(r'[^А-ЯЁа-яё0-9.,:;\\/\-\n\(\)\{\}\[\]*?!@#=+\^%$ ]', content))
        stats[f] = foreign / (foreign + russian)
    
    stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[1])}
    filtered = dict(filter(lambda s: s[1] < foreign_threshold, stats.items()))
    return set(filtered.keys()), {
        'foreign': {
            'foreign_threshold': foreign_threshold,
            'len': len(filtered),
            'time': time_since(now),
            'stats': stats
    }}


def frequent(input_files, stopwords, cpu_count, frequent_words, frequent_threshold, grams_n, tqdm_conf):
    now = time.time()

    fn = Preprocess(stopwords, grams_n)
    len_files = len(input_files)
    with Pool(cpu_count) as p:
        file_words = list(tqdm(p.imap(fn, input_files), desc='gen-frequent', total=len_files, **tqdm_conf))

    stats = {}
    for f, t in tqdm(file_words, desc='frequent', **tqdm_conf):
        score = 0
        for k, v in frequent_words.items():
            if k in t:
                score += v
        stats[f] = score

    stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[1])}
    filtered = dict(filter(lambda s: s[1] > frequent_threshold, stats.items()))
    return set(filtered.keys()), {
        'frequent': {
            'frequent_threshold': frequent_threshold,
            'len': len(filtered),
            'time': time_since(now),
            'stats': stats
    }}


class Preprocess:
    def __init__(self, stopwords, n):
        Preprocess.n = n
        Preprocess.stopwords = stopwords
        Preprocess.lemmatizer = Mystem()
        Preprocess.regex = compile({
            'args': {},
            'expr': r'[А-ЯЁа-яё]{3,}',
            'groups': (0,),
        })
    
    @classmethod
    def __call__(cls, file):
        text = read_lines(file)
        matches = regex_match(Preprocess.regex, text)
        lemmatized = [cls.lemmatizer.lemmatize(m['groups'][0].lower())[0] for m in matches]
        stopped = [l for l in lemmatized if l not in cls.stopwords]
        stopped_n = len(stopped)
        ngrams = set()
        for i in range(2, Preprocess.n):
            for j in range(stopped_n - i):
                ngrams.add(' '.join(stopped[j:j+i]))
                
        return file, list(ngrams)
    