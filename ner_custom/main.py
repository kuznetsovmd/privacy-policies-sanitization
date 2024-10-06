import os
import pandas as pd

from tqdm import tqdm

from utils.fsys import list_files, read_lines
from utils.regexes import default_criterion, regex_match, merge_matches


def main(input_docs, per_blacklist, loc_blacklist, tasks, tqdm_conf):
    all_matches = []
    for f in tqdm(list_files(input_docs), **tqdm_conf):
        text = read_lines(f)

        for t in tasks:
            found = find_matches(text, t['dataset'], t['regexes'])
            all_matches.extend([(f, 'custom', t['type'], ' '.join(g)) for m in merge_matches(found, default_criterion) for g in m['groups']])

    df = pd.DataFrame(all_matches, columns=['file', 'library', 'type', 'value'])
    df.to_csv('resources/csv_raw/custom.csv')

    if not os.path.exists(per_blacklist):
        blacklist_per = df[df['type'] == 'per'].copy()
        blacklist_per['value'] = blacklist_per['value'].str.split(r'[^а-яёА-ЯЁ]', regex=True)
        blacklist_per = blacklist_per.explode('value')
        blacklist_per = blacklist_per[blacklist_per['value'].str.len() > 0]
        blacklist_per = blacklist_per.drop_duplicates()[['file', 'value']].groupby(['value']).count().sort_values('file', ascending=False)
        blacklist_per.to_csv(per_blacklist)

    if not os.path.exists(loc_blacklist):
        blacklist_loc = df[df['type'] == 'loc'].copy()
        blacklist_loc['value'] = blacklist_loc['value'].str.split(r'[^а-яёА-ЯЁ]', regex=True)
        blacklist_loc = blacklist_loc.explode('value')
        blacklist_loc = blacklist_loc[blacklist_loc['value'].str.len() > 0]
        blacklist_loc = blacklist_loc.drop_duplicates()[['file', 'value']].groupby(['value']).count().sort_values('file', ascending=False)
        blacklist_loc.to_csv(loc_blacklist)
    

def find_matches(text, dataset, regexes):
    matches = []
    for _, r in enumerate(regexes):
        for match in regex_match(r, text):
            groups = set(g.replace('ё', 'е').replace('.', '') for g in match['groups'])

            if all(len(g) <= 1 for g in groups):
                continue
            
            if groups.issubset(dataset):
                matches.append(match)

    return matches
    