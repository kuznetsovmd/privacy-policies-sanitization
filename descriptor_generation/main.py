

import json
import os
import shutil

from tqdm import tqdm

from utils.fsys import list_files


def calc_stat(stats):
    length = stats['len']
    ol = stats['ol'] if 'ol' in stats else 0
    ul = stats['ul'] if 'ul' in stats else 0
    li = stats['li'] if 'li' in stats else 0
    table = stats['table'] if 'table' in stats else 0
    paragraphs = \
        (stats['p'] if 'p' in stats else 0) \
        + (stats['div'] if 'div' in stats else 0)
    headings = \
        (stats['h1'] if 'h1' in stats else 0) \
        + (stats['h2'] if 'h2' in stats else 0) \
        + (stats['h3'] if 'h3' in stats else 0) \
        + (stats['h4'] if 'h4' in stats else 0) \
        + (stats['h5'] if 'h5' in stats else 0) \
        + (stats['h6'] if 'h6' in stats else 0)
    
    return {
        'length': length,
        'ol': ol,
        'ul': ul,
        'li': li,
        'table': table,
        'br': paragraphs,
        'p': headings,
    }


def main(input_files, old_descriptor, new_descriptor, old_metrics,
        new_metrics, statistics_file, output_files, tqdm_conf):
    shutil.copy(old_metrics, new_metrics)
    basenames = {os.path.basename(f): f for f in list_files(input_files)}

    with open(old_descriptor,'r') as s:
        d = json.load(s)

    with open(statistics_file,'r') as s:
        s = {os.path.basename(f): s for f, s in json.load(s).items()}

    hashes = set()
    descriptor = []
    for r in tqdm(d, desc='make_descriptor', **tqdm_conf):
        filename = f'{r["original_policy"]}.md'
        new_filename = f'{r["policy_hash"]}.md'
        if filename in basenames:
            shutil.copy(basenames[filename], f'{output_files}/{new_filename}')
            hashes.add(r['policy_hash'])
            descriptor.append({
                'id': r['id'], 
                'policy_hash': r['policy_hash'], 
                'output_policy': new_filename,
                'statistics': calc_stat(s[filename]),
            })

    with open(new_descriptor,'w') as s:
        json.dump(descriptor, s, indent=4)
