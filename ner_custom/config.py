import os
import sys
from ner_custom.regexes import dataset_regexes, names_regexes, toponyms_regexes
from ner_custom.data import create_from_dataset, create_from_phias, create_from_policies, preprocess_dataset, read_dataset, save_dataset, update_list
from utils.fsys import make_paths


# https://www.google.com/url?sa=i&url=https%3A%2F%2Fngodata.ru%2Fdataset%2Frussiannames&psig=AOvVaw0kZkdtRG2lQ7pMt6okDn16&ust=1713394692409000&source=images&cd=vfe&opi=89978449&ved=0CAgQr5oMahcKEwiAtr3h6seFAxUAAAAAHQAAAAAQBA
# https://www.kaggle.com/datasets/rai220/russian-cyrillic-names-and-sex
def conf(resources, tqdm_conf, **kwargs):
    input_docs = f'{resources}/sanitized_html/*.*'

    persons_dataset = f'{resources}/persons.txt'
    if not os.path.exists(persons_dataset):

        names = create_from_policies(input_docs, dataset_regexes(), tqdm_conf)
        
        names.update(create_from_dataset([
            '/mnt/Source/kuznetsovmd/__datasets/names-dataset/surnames_table.jsonl',
            '/mnt/Source/kuznetsovmd/__datasets/names-dataset/names_table.jsonl',
            '/mnt/Source/kuznetsovmd/__datasets/names-dataset/midnames_table.jsonl'
        ]))
        
        names = preprocess_dataset(
            names,
            update_list(f'{resources}/whitelist.txt'),
            update_list(f'{resources}/blacklist.txt',
                        [f'{c}' for c in 'абвгдеёжзийклмнопрстуфхцчшщэюя']))

        save_dataset(persons_dataset, names)

    locations_dataset = f'{resources}/locations.txt'
    if not os.path.exists(locations_dataset):
        locations = preprocess_dataset(
            create_from_phias('/mnt/Windows/__phias/**/AS_ADDR_OBJ_20240408_*.XML', tqdm_conf), [], [])
        save_dataset(locations_dataset, locations)

    inputs = {
        'input_docs': input_docs,
        'tasks': [{
                'dataset': read_dataset(persons_dataset),
                'regexes': names_regexes(),
            }, {
                'dataset': read_dataset(locations_dataset),
                'regexes': toponyms_regexes(),
        }],
        'tqdm_conf': tqdm_conf
    }

    outputs = {
        'output_docs': f'{resources}/ner_removed',
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
