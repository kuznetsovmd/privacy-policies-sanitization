

def conf(resources, tqdm_conf, **kwargs):
    inputs = {
        'input_docs': f'{resources}/sanitized_html/*.*',
        'output_file': f'{resources}/natasha.json', 
        'cpu_count': 12,
        'tqdm_conf': tqdm_conf,
    }

    return { **inputs  }
