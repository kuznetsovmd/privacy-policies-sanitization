

from hashlib import md5
import json
import os

from tqdm import tqdm

from utils.fsys import list_files


def make_descriptor(input_files, old_descriptor, new_descriptor, tqdm_conf):
    filenames = {os.path.basename(f) for f in list_files(input_files)}

    with open(old_descriptor,'r') as plain:
        desc = json.load(plain)

    deprecated_keys = {'website', 'policy', 'original_policy', 'original_policy', 'processed_policy', 'plain_policy'}
    hashes = set()
    new_desc = []
    for r in tqdm(desc, desc='make_descriptor', **tqdm_conf):
        if r['plain_policy'] in filenames and r['policy_hash'] not in hashes:
            n = {k: v for k, v in r.items() if k not in deprecated_keys}
            new_desc.append({**n, 'output_policy': md5(r['plain_policy'].encode('utf-8')).hexdigest()})
            hashes.add(r['policy_hash'])

    with open(new_descriptor,'w') as outpt_json:
        desc = json.dump(new_desc, outpt_json, indent=4)
