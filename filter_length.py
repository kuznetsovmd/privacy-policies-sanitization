import sys
import os

from docs import *


FILES = f'{RESOURCES}/sanitized_policies/'
FILTERED_LENGHT = f'{RESOURCES}/output_policies/'

def process_paragraphs(doc):
    content = read_lines(f'{FILES}/{doc}')

    if len(content) > 500:
        with open(f'{FILTERED_LENGHT}/{doc}', 'w') as d:
            d.write(content)


def main():
    files = {os.path.basename(f) for f in find_files(f'{FILES}/*.txt')}

    list(map(process_paragraphs, files))
    return 0
    

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('EXIT')
        sys.exit(130)