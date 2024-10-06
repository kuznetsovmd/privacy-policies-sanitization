import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
from transformers import AutoTokenizer, BertForTokenClassification
from transformers import pipeline

from utils.fsys import read_lines
from utils.fsys import list_files, read_lines


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
        

def process(docs, tqdm_conf):
    tokenizer = AutoTokenizer.from_pretrained("0x7o/rubert-base-massive-ner", truncation=True, model_max_length=512, add_special_tokens=True)
    model = BertForTokenClassification.from_pretrained("0x7o/rubert-base-massive-ner")
    nlp = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="max")

    output = []
    for file, spans in tqdm(docs.items(), total=len(docs), **tqdm_conf):
        for r in nlp(spans):
            if r['entity_group'] == 'person':
                output.append((file, 'transformers', 'per', r['word']))
            if r['entity_group'] == 'place_name':
                output.append((file, 'transformers', 'loc', r['word']))

    return output


class Preprocess:
    @classmethod
    def __call__(cls, file):
        return file, read_lines(file)
