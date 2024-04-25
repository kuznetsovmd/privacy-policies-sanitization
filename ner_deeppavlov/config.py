

from utils.fsys import make_paths
from utils.model import select_device


def ner_conf(resources, use_cuda, tqdm_conf, **kwargs):
    _ = select_device(use_cuda)
    
    inputs = {
        'input_docs': f'{resources}/sanitized_html/*.md',
        'tqdm_conf': tqdm_conf
    }

    outputs = {
        'ner_removed': f'{resources}/ner_removed'
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
