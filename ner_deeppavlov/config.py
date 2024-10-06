

def conf(resources, tqdm_conf, **kwargs):
    ner_res = f'{resources}/ner'
    
    inputs = {
        'input_docs': f'{resources}/sanitization_results/*.*',
        'output_file': f'{ner_res}/deeppavlov.csv', 
        'cpu_count': 12,
        'tqdm_conf': tqdm_conf
    }

    return { **inputs }
