import json
import re
import numpy as np
from tqdm import tqdm
from transformers import logging
from multiprocessing import Pool
from tqdm import tqdm
from utils.fsys import read_lines
from utils.regexes import regex_match, compile
import nltk

from utils.fsys import list_files, read_lines
from ner_deeppavlov.data import add_pad, boundries

from deeppavlov import configs, build_model
from deeppavlov.core.commands.utils import parse_config
from deeppavlov.core.models.component import Component


class splitter(Component):
    def __init__(self, *args,**kwargs) -> None:
        super().__init__()

    def __call__(self, x_tokens, x_subword_tokens, x_subword_tok_ids, startofword_markers, attention_mask, tokens_offsets, **kwargs):
        r1, r2, r6 = \
            self.split_list(x_tokens[0], 512, '[PAD]'),\
            self.split_list(x_subword_tokens[0], 512, '[PAD]'),\
            self.split_list(tokens_offsets[0], 512, (0, 0))

        r3, r4, r5 = \
            self.split_array(x_subword_tok_ids[0], 512, 100),\
            self.split_array(startofword_markers[0], 512, 0),\
            self.split_array(attention_mask[0], 512, 0),
        
        return r1, r2, r3, r4, r5, r6

    @staticmethod
    def split_list(array, n, pad):
        splitted = []
        for i in range(0, len(array), n):
            n_pad = n - len(array) % n
            splitted.append(array[i:i + n])
            if n_pad:
                splitted[-1].extend([pad] * n_pad)
        return splitted

    @staticmethod
    def split_array(array, n, pad):
        n_pad = n - len(array) % n
        return np.reshape([*array, *([pad] * n_pad)], (-1, n))

    def reset(self):
        ...

    def destroy(self):
        ...


def main(input_docs, output_file, cpu_count, tqdm_conf):

    config_dict = parse_config(configs.ner.ner_collection3_bert)
    
    config_dict['chainer']['out'] = ['x_tokens', 'y_pred', 'tokens_offsets']
    config_dict['chainer']['pipe'][0]['max_seq_length'] = None
    config_dict['chainer']['pipe'][0]['do_lower_case'] = False
    config_dict['chainer']['pipe'].insert(1, {
        'class_name': 'ner_deeppavlov.main:splitter',
        'in': ['x_tokens', 'x_subword_tokens', 'x_subword_tok_ids', 'startofword_markers', 'attention_mask', 'tokens_offsets'],
        'out': ['x_tokens', 'x_subword_tokens', 'x_subword_tok_ids', 'startofword_markers', 'attention_mask', 'tokens_offsets'],
    })
        
    log_level = logging.get_verbosity()
    logging.set_verbosity(logging.ERROR)
    ner_model = build_model(config_dict, download=False, install=False, load_trained=True)
    logging.set_verbosity(log_level)
    
    output = []
    for d in tqdm(list_files(input_docs), desc='Docs', **tqdm_conf):
        text = read_lines(d)
        _, pred, offsets = ner_model([text])

        pers, locs = set(), set()
        for p, o in zip(pred, offsets):
            for s, e in boundries(add_pad(p, 'O'), add_pad(o, (0, 0)), ['B-PER', 'I-PER']):
                output.append((d, 'deeppavlov', 'per', text[s:e]))
            for s, e in boundries(add_pad(p, 'O'), add_pad(o, (0, 0)), ['B-LOC', 'I-LOC']):
                output.append((d, 'deeppavlov', 'loc', text[s:e]))

    df = pd.DataFrame(matches, columns=['file', 'library', 'type', 'value'])
    df.to_csv(output_file)


def preprocess(input_files, tqdm_conf, cpu_count):
    nltk.download("stopwords")

    fn = Preprocess()
    with Pool(cpu_count) as p:
        texts_list = tqdm(p.imap(fn, input_files), desc='preprocess', total=len(input_files), **tqdm_conf)
        texts_list = {f: t for f, t in list(texts_list)}

    return texts_list
    