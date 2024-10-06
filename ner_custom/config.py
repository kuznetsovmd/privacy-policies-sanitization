import os
import pandas as pd
import sys
from ner_custom.regexes import dataset_regexes, ngrams_regexes
from ner_custom.data import create_from_dataset, create_from_phias, create_from_policies, process_with_petrovich, read_dataset, save_dataset
from utils.fsys import make_paths


def conf(resources, tqdm_conf, **kwargs):
    ner_res = f'{resources}/ner'
    input_docs = f'{resources}/sanitization_results/*.*'

    custom_vocab = f'{ner_res}/custom_vocab.csv'
    if not os.path.exists(custom_vocab):
        names = set()
        names.update(create_from_policies(input_docs, dataset_regexes(), tqdm_conf))
        names.update(create_from_dataset('/mnt/Source/kuznetsovmd/datasets/names-dataset/surnames_table.jsonl'))
        names.update(create_from_dataset('/mnt/Source/kuznetsovmd/datasets/names-dataset/names_table.jsonl'))
        names.update(create_from_dataset('/mnt/Source/kuznetsovmd/datasets/names-dataset/midnames_table.jsonl'))
        names.update(process_with_petrovich(names))
        names.update(c for c in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ')
        names_df = pd.DataFrame([('per', n) for n in names], columns=['type', 'value'])

        locations = set()
        locations.update(create_from_phias('/mnt/Windows/__phias/**/AS_ADDR_OBJ_20240408_*.XML', tqdm_conf))
        locations_df = pd.DataFrame([('loc', l) for l in locations], columns=['type', 'value'])

        all_ne = pd.concat([names_df, locations_df], ignore_index=True)
        all_ne['value'] = all_ne['value'].str.split(r'[^а-яёА-ЯЁ]', regex=True)
        all_ne = all_ne.explode('value')
        all_ne = all_ne[all_ne['value'].str.len() > 0].drop_duplicates().reset_index(drop=True)
        all_ne.to_csv(custom_vocab)
    else:
        all_ne = pd.read_csv(custom_vocab)

    inputs = {
        'input_docs': input_docs,
        'per_blacklist': f'{ner_res}/blacklist_pers.csv',
        'loc_blacklist': f'{ner_res}/blacklist_locs.csv',
        'tasks': [{
            'dataset': set(all_ne[all_ne['type'] == 'per']['value'].tolist()),
            'regexes': ngrams_regexes(),
            'type': 'per'
        }, {
            'dataset': set(all_ne[all_ne['type'] == 'loc']['value'].tolist()),
            'regexes': ngrams_regexes(),
            'type': 'loc'
        }],
        'tqdm_conf': tqdm_conf
    }

    return { **inputs }
