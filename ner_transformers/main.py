import re
import json
from multiprocessing import Pool
from tqdm import tqdm
from transformers import AutoTokenizer, BertForTokenClassification
from transformers import pipeline

from utils.fsys import read_lines
from utils.regexes import regex_match, compile
from utils.fsys import list_files, read_lines


def main(input_docs, output_file, cpu_count, tqdm_conf):
    texts = preprocess(list_files(input_docs), tqdm_conf, cpu_count)
    matches = process(texts, tqdm_conf)
    with open(output_file, 'w') as s:
        json.dump(matches, s, ensure_ascii=False, indent=4)


def preprocess(input_files, tqdm_conf, cpu_count):
    fn = Preprocess()
    with Pool(cpu_count) as p:
        texts_list = tqdm(p.imap(fn, input_files), desc='preprocess', total=len(input_files), **tqdm_conf)
        texts_list = {f: t for f, t in list(texts_list)}
    return texts_list
        

def process(docs, tqdm_conf):
    tokenizer = AutoTokenizer.from_pretrained("0x7o/rubert-base-massive-ner", truncation=True, model_max_length=512, add_special_tokens=True)
    model = BertForTokenClassification.from_pretrained("0x7o/rubert-base-massive-ner")
    nlp = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="max")

    output = {}
    for file, spans in tqdm(docs.items(), total=len(docs), **tqdm_conf):
        pers, locs = set(), set()
        for res in nlp(spans):
            for r in res:
                if r['entity_group'] == 'person':
                    pers.add(r['word'])
                if r['entity_group'] == 'place_name':
                    locs.add(r['word'])

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
