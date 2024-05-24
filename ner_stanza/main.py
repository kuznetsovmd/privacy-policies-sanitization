import re
import json
import stanza
from multiprocessing import Pool
from tqdm import tqdm

from utils.fsys import read_lines
from utils.regexes import regex_match, compile
from utils.fsys import list_files, read_lines
import torch
from torch import device as get_device
from torch.cuda import current_device, is_available


def main(input_docs, output_file, cpu_count, tqdm_conf):
    texts = preprocess(list_files(input_docs), tqdm_conf, cpu_count)
    matches = process(texts, tqdm_conf, 12)
    with open(output_file, 'w') as s:
        json.dump(matches, s, ensure_ascii=False, indent=4)


def preprocess(input_files, tqdm_conf, cpu_count):
    fn = Preprocess()
    with Pool(cpu_count) as p:
        texts_list = tqdm(p.imap(fn, input_files), desc='preprocess', total=len(input_files), **tqdm_conf)
        texts_list = {f: t for f, t in list(texts_list)}
    return texts_list


def select_device(use_cuda):
    d = current_device() if is_available() and use_cuda else get_device('cpu')
    print(f'Torch version: {torch.__version__}')
    try:
        print(f'Using: {torch.cuda.get_device_name(d)}')
    except ValueError:
        print(f'Using: CPU')
    return d
        

def process(docs, tqdm_conf, cpu_count):
    stanza.download('ru') 
    nlp = stanza.Pipeline('ru', processors='tokenize,ner') 

    output = {}
    for file, spans in tqdm(docs.items(), total=len(docs), **tqdm_conf):
        pers, locs = set(), set()
        for s_ in spans:
            doc = nlp(s_)
            for el in doc.sentences:
                for ent in el.entities:
                    if ent.type == 'PERSON' \
                            or ent.type == 'PER' \
                            or ent.type == 'PERS' \
                            or ent.type == 'PNAME':
                        pers.add(ent.text)
                    if ent.type == 'LOC' \
                            or ent.type == 'GPE':
                        locs.add(ent.text)

        output[file] = {'pers': list(pers), 'locs': list(locs)}
    return output


class Preprocess:
    def __init__(self):
        Preprocess.regex = compile({
            'args': {'flags': re.MULTILINE},
            'expr': r'^[^А-ЯЁа-яёA-Za-z]*([А-ЯЁа-яёA-Za-z\d:;!? ,.\-\\\/(){}\[\]]+)',
            'groups': (1,),
        })
    
    @classmethod
    def __call__(cls, file):
        text = read_lines(file)
        matches = regex_match(Preprocess.regex, text)
        return file, [m['groups'][0] for m in matches]
