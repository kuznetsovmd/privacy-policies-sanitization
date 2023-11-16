import sys
import os
import json

from docs import *


OUTPUT = f'{RESOURCES}/output_policies/'
PREV_DESC = '../privacy-policies-in-russian/json/plain.json'
NEXT_DESC = '../privacy-policies-in-russian/json/output.json'


def main():
    output = {os.path.basename(f) for f in find_files(f'{OUTPUT}/*.txt')}

    desc = None
    with open(PREV_DESC, 'r') as plain:
        desc = json.load(plain)

    new_desc = []
    for r in desc:
        if r['plain_policy'] in output:
            r['output_policy'] = r["plain_policy"]
            new_desc.append(r.copy())

    with open(NEXT_DESC, 'w') as outpt_json:
        desc = json.dump(new_desc, outpt_json, indent=4)
        
    return 0
    

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('EXIT')
        sys.exit(130)
