import json

from tqdm import tqdm

from utils.fsys import list_files, read_lines

from petrovich.main import Petrovich
from petrovich.enums import Case, Gender

from utils.regexes import regex_match


def create_from_dataset(names_dataset):
    names = set()
    for nd in names_dataset:
        with open(nd, 'r') as ds:
            names.update([n for l in ds.read().splitlines() for n in json.loads(l)['text'].split(' ')])
    return names


def create_from_policies(input_docs, regexes, tqdm_conf):
    all_matches = []
    for f in tqdm(list_files(input_docs), **tqdm_conf):
        text = read_lines(f)
        for i, r in enumerate(regexes):
            for o in regex_match(r, text):
                o['regex_id'] = i
                o['filename'] = f
                all_matches.append(o)
    
    return all_matches, set(g for m in all_matches for g in m['groups'] if g)


def preprocess_dataset(names, whitelist, blacklist):
    p = Petrovich()
    names = set(r.lower() for r in names if '.' not in r and r)
    names.update([b.lower() for b in blacklist])
    names = set(p.lastname(n, c, g) for n in names for g in [Gender.MALE, Gender.FEMALE] for c in Case.CASES)
    names = names.difference([w.lower() for w in whitelist])
    return set(r.replace('ё', 'е') for r in names)


def save_dataset(file, data):
    with open(file, 'w') as f:
        f.write('\n'.join(data))


def read_dataset(file):
    with open(file, 'r') as f:
        return set(f.read().split())
    

def update_list(path, new=()):
    with open(path) as f:
        l = [*new, *f.read().splitlines()]
    with open(path, 'w') as f:
        f.write('\n'.join(sorted(set(l))).lower())
    return l
        