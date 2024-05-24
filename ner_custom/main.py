import os

from tqdm import tqdm
from collections import Counter
from nltk.stem import SnowballStemmer

from utils.fsys import list_files, read_lines
from utils.regexes import replace_matches, default_criterion, regex_match, merge_matches


def main(input_docs, output_docs, tasks, tqdm_conf):
    all_matches = []
    all_misses = []
    for f in tqdm(list_files(input_docs), **tqdm_conf):
        text = read_lines(f)
        matches = []
        for t in tasks:
            misses, found = find_matches(text, t['dataset'], t['regexes'])
            matches.extend(merge_matches(found, default_criterion))
            matches = [{**m, 'filename': f} for m in matches]
            all_misses.extend(misses)
        all_matches.extend(matches)
        
        with open(f'{output_docs}/{os.path.basename(f)}', 'w') as f:
            f.write(replace_matches(text, matches))

    stats = {
        'filenames': Counter([m['filename'] for m in all_matches]),
        'groups': Counter([m['groups'] for m in all_matches])
    }
    
    print('\n'.join(f'{m["coords"].__str__():<16}: {m["groups"]}' for m in all_matches))


def find_matches(text, dataset, regexes):
    snowball = SnowballStemmer(language="russian")
    matches = []
    misses = []
    for i, r in enumerate(regexes):
        for match in regex_match(r, text):
            match['regex_id'] = i
            match['sub'] = r['sub']
            groups = set(snowball.stem(g.lower().replace('ё', 'е').replace('.', '')) for g in match['groups'])

            if all(len(g) <= 1 for g in groups):
                continue
            
            if groups.issubset(dataset):
                matches.append(match)
            elif groups.intersection(dataset):
                misses.append(tuple(groups))

    return misses, matches
    