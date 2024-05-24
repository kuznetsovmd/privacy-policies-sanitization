import json
import os
import re
import time

from tqdm import tqdm
from hashlib import md5
from multiprocessing import Pool

from html_sanitization.frequent import frequent
from html_sanitization.sanitize import Sanitize
from utils.fsys import list_files, read_lines
from utils.timing import time_since


def main(input_files, sanitization_statistics_file, structure_statistics_file, 
            cpu_count, sanitizer_conf, deprecated_rules, sanitized_files, uppercase_threshold, 
            short_threshold, foreign_threshold, stopwords_file, words_cnt, tqdm_conf):
    start = time.time()

    files = set(list_files(input_files))
    statistics = {
        'total_input_docs': {'len': len(files)}
    }
    
    now = time.time()
    remove = deprecated(files, tqdm_conf, deprecated_rules)
    files = files.difference(remove)
    statistics = {**statistics,
        'deprecated': {
            'len': len(files),
            'time': time_since(now),
    }}

    now = time.time()
    fn = Sanitize(sanitized_files, **sanitizer_conf)
    with Pool(cpu_count) as p:
        output = list(tqdm(p.imap(fn, files), desc='sanitize', total=len(files), **tqdm_conf))

    stats = {file: stats for file, stats in output}
    with open(structure_statistics_file, 'w') as s:
        json.dump(stats, s, ensure_ascii=False, indent=4)

    files = set(file for file, _ in output)
    statistics = {**statistics,
        'sanitize': {
            'len': len(files),
            'time': time_since(now),
    }}

    now = time.time()
    remove = short(files, tqdm_conf, short_threshold)
    statistics = {**statistics,
        'short': {
            'short_threshold': short_threshold, 
            'len': len(files.difference(remove)),
            'time': time_since(now),
    }}

    now = time.time()
    remove.update(duplicates(files.difference(remove), tqdm_conf))
    statistics = {**statistics,
        'duplicates': {
            'len': len(files.difference(remove)),
            'time': time_since(now),
    }}

    now = time.time()
    remove.update(uppercase(files.difference(remove), tqdm_conf, uppercase_threshold))
    statistics = {**statistics,
        'uppercase': {
            'uppercase_threshold': uppercase_threshold, 
            'len': len(files.difference(remove)),
            'time': time_since(now),
    }}

    now = time.time()
    remove.update(foreign(files.difference(remove), tqdm_conf, foreign_threshold))
    statistics = {**statistics,
        'foreign': {
            'foreign_threshold': foreign_threshold, 
            'len': len(files.difference(remove)),
            'time': time_since(now),
    }}

    now = time.time()
    words, filtered = frequent(files.difference(remove), tqdm_conf, read_lines(stopwords_file).split(), cpu_count, words_cnt)
    remove.update(filtered)
    statistics = {**statistics,
        'frequent': {
            'words_cnt': words_cnt,
            'words': words, 
            'len': len(files.difference(remove)),
            'time': time_since(now),
    }}
    
    for f in remove:
        os.remove(f)

    now = time.time()
    statistics = {**statistics,
        'total_output_docs': {
            'cpu_count': cpu_count,
            'len': len(files.difference(remove)),
            'time': time_since(now),
            'total_time': time_since(start),
    }}

    with open(sanitization_statistics_file, 'w') as s:
        json.dump(statistics, s, ensure_ascii=False, indent=4)


def deprecated(input_files, tqdm_conf, deprecated_rules):
    filtered = set()
    for f in tqdm(input_files, desc='deprecated', **tqdm_conf):
        if any(rule(f) for rule in deprecated_rules):
            filtered.add(f)
    return filtered


def short(input_files, tqdm_conf, short_threshold=500): 
    filtered = set()
    for f in tqdm(input_files, desc='short', **tqdm_conf):
        if len(read_lines(f)) < short_threshold:
            filtered.add(f)
    return filtered


def duplicates(input_files, tqdm_conf):
    duplicates = set()
    unique = set()
    for f in tqdm(input_files, desc='duplicates', **tqdm_conf):
        content = read_lines(f)
        hash = md5(content.encode('utf-8')).hexdigest()
        if hash in unique:
            duplicates.add(f)
        unique.add(hash)
    return duplicates


def uppercase(input_files, tqdm_conf, uppercase_threshold=.1):
    filtered = set()
    for f in tqdm(input_files, desc='uppercase', **tqdm_conf):
        content = read_lines(f)
        upper = sum(1 for c in content if c.isupper())
        lower = sum(1 for c in content if c.islower())
        if upper / (upper + lower) > uppercase_threshold:
            filtered.add(f)
    return filtered


def foreign(input_files, tqdm_conf, foreign_threshold=.3):
    filtered = set()
    for f in tqdm(input_files, desc='foreign', **tqdm_conf):
        content = read_lines(f)
        russian = len(re.findall(r'[А-ЯЁа-яё]', content))
        foreign = len(re.findall(r'[^А-ЯЁа-яё0-9.,:;\\/\-\n\(\)\{\}\[\]*?!@#=+\^%$ ]', content))
        if foreign / (foreign + russian) > foreign_threshold:
            filtered.add(f)
    return filtered
