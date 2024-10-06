import pandas as pd
import stanza
from multiprocessing import Pool
from tqdm import tqdm

from utils.fsys import read_lines
from utils.fsys import list_files, read_lines
import torch
from torch import device as get_device
from torch.cuda import current_device, is_available


def main(input_docs, output_file, cpu_count, tqdm_conf):
    texts = preprocess(list_files(input_docs), tqdm_conf, cpu_count)
    matches = process(texts, tqdm_conf)
    df = pd.DataFrame(matches, columns=['file', 'library', 'type', 'value'])
    df.to_csv(output_file)


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
        

def process(docs, tqdm_conf):
    stanza.download('ru') 
    nlp = stanza.Pipeline('ru', processors='tokenize,ner', use_gpu=True) 

    output = []
    for file, spans in tqdm(docs.items(), total=len(docs), **tqdm_conf):
        for s_ in spans:
            doc = nlp(s_)
            for el in doc.sentences:
                for ent in el.entities:
                    if ent.type == 'PERSON' \
                            or ent.type == 'PER' \
                            or ent.type == 'PERS' \
                            or ent.type == 'PNAME':
                        output.append((file, 'stanza', 'per', ent.text))
                    if ent.type == 'LOC' \
                            or ent.type == 'GPE':
                        output.append((file, 'stanza', 'loc', ent.text))

    return output


class Preprocess:
    @classmethod
    def __call__(cls, file):
        return file, read_lines(file).split('\n')
