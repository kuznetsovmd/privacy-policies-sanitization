import json

from tqdm import tqdm

from petrovich.main import Petrovich
from petrovich.enums import Case, Gender
from utils.fsys import list_files, read_lines
from utils.regexes import regex_match, compile


def create_from_dataset(dataset):
    return set(n for l in read_lines(dataset).splitlines() for n in json.loads(l)['text'].split(' '))


def process_with_petrovich(dataset):
    pvch = Petrovich()

    cases = Case.CASES
    genders = (Gender.MALE, Gender.FEMALE)

    dataset = set(d for d in dataset)
    dataset = set(d.replace('.', ' ').replace('-', ' ') for d in dataset)
    dataset = set(w for d in dataset for w in d.split())

    variants = set()
    for item in dataset:
        for c in cases:
            for g in genders:
                variants.update((
                    pvch.firstname(item, c, g),
                    pvch.lastname(item, c, g),
                    pvch.middlename(item, c, g)))

    dataset.update(variants)
    dataset.update(set(w.upper() for w in dataset))

    return set(d for d in dataset if d)


def create_from_policies(input_docs, regexes, tqdm_conf):
    all_matches = []
    for f in tqdm(list_files(input_docs), **tqdm_conf):
        text = read_lines(f)
        for i, r in enumerate(regexes):
            for o in regex_match(r, text):
                all_matches.append(o)
    return set(g for m in all_matches for g in m['groups'] if g)
        

def create_from_phias(phias_dataset, tqdm_conf):
    files = list_files(phias_dataset)
    regex = compile({
        'args': {},
        'expr': r'<[^<>]+NAME=\"([А-ЯЁа-яё\- .]+)\"[^<>]+TYPENAME=\"([А-ЯЁа-яё\- .]+)\"[^<>]+>',
        'groups': (2, 1)
    })

    locations = set()
    for f in tqdm(files, **tqdm_conf):
        text = read_lines(f)
        matches = regex_match(regex, text)
        locations.update(g for m in matches for g in m['groups'])

    # PYMORPHY

    return locations


def save_dataset(file, data):
    with open(file, 'w') as f:
        f.write('\n'.join(data))


def read_dataset(file):
    with open(file, 'r') as f:
        return set(f.read().split())
    