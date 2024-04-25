from collections import Counter
import os
from pprint import pprint
import sys
from ner_custom.regexes import dataset_regexes, names_regexes, toponyms_regexes
from ner_custom.data import create_from_dataset, create_from_policies, preprocess_dataset, read_dataset, save_dataset, update_list
from utils.fsys import make_paths

# Телефоны с ///, бильбюли оглы
# https://www.google.com/url?sa=i&url=https%3A%2F%2Fngodata.ru%2Fdataset%2Frussiannames&psig=AOvVaw0kZkdtRG2lQ7pMt6okDn16&ust=1713394692409000&source=images&cd=vfe&opi=89978449&ved=0CAgQr5oMahcKEwiAtr3h6seFAxUAAAAAHQAAAAAQBA
# https://www.kaggle.com/datasets/rai220/russian-cyrillic-names-and-sex
def ner_conf(resources,tqdm_conf, **kwargs):
    input_docs = f'{resources}/sanitized_html/*.html'

    dataset = f'{resources}/names.txt'
    if not os.path.exists(dataset):

        found, names = create_from_policies(input_docs, dataset_regexes(), tqdm_conf)
        # pprint([f['groups'] for f in found])
        # pprint(Counter([f['groups'] for f in found]))
        # sys.exit(0)
        
        names.update(create_from_dataset([
            '/mnt/Source/kuznetsovmd/__datasets/nms_dataset/surnames_table.jsonl',
            '/mnt/Source/kuznetsovmd/__datasets/nms_dataset/names_table.jsonl',
            '/mnt/Source/kuznetsovmd/__datasets/nms_dataset/midnames_table.jsonl'
        ]))
        
        names = preprocess_dataset(
            names,
            update_list(f'{resources}/whitelist.txt'),
            update_list(f'{resources}/blacklist.txt',
                        [f'{c}' for c in 'абвгдеёжзийклмнопрстуфхцчшщэюя']))

        save_dataset(dataset, names)

    inputs = {
        'input_docs': input_docs,
        'tasks': [{
                'dataset': read_dataset(dataset),
                'regexes': names_regexes(),
            }, {
                'dataset': set(),
                'regexes': toponyms_regexes(),
        }],
        'tqdm_conf': tqdm_conf
    }

    outputs = {
        'output_docs': f'{resources}/ner_removed',
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
