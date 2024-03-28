import os
import json

from utils.fsys import list_files


def make_descriptor(output_files, old_descriptor, new_descriptor):
    output = {os.path.basename(f) for f in list_files(f'{output_files}/*.txt')}

    desc = None
    with open(old_descriptor, 'r') as plain:
        desc = json.load(plain)

    hashes = set()
    new_desc = []
    for r in desc:
        if r['plain_policy'] in output and r['policy_hash'] not in hashes:
            r['output_policy'] = r["plain_policy"]
            new_desc.append(r.copy())
            hashes.add(r['policy_hash'])

    with open(new_descriptor, 'w') as outpt_json:
        desc = json.dump(new_desc, outpt_json, indent=4)
