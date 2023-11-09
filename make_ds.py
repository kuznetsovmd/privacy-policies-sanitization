import sys
import os
from getkey import getkey

from docs import *


NOT_LABELED = f'{RESOURCES}/for_sanitization/'
LABELED = f'{RESOURCES}/sanitization_docs/'
LABELS = f'{RESOURCES}/sanitization_labels/'


class Choice:
    ACCEPT = 1
    DECLINE = 2


def ask(message, replies):
    print(message)
    while True:
        try:
            key = getkey()
            return replies[key]
        except KeyError:
            print('Wrong key!')


def process_paragraphs(doc):
    print(f'\n\n{"=" * 120}')
    labels = []
    lines = read_lines(f'{NOT_LABELED}/{doc}')
    for i, p in enumerate(lines.split('\n\n')):
        print(f'\n\n>>> {doc} > paragraph {i}\n\n{p}', end='\n\n')
        a = ask('> Do you want to accept this paragraph? y/[n]', {'y': Choice.ACCEPT, 'n': Choice.DECLINE})
        if a == Choice.ACCEPT:
            labels.append('Yes')
            print('\n> Accepted')
        elif a == Choice.DECLINE:
            labels.append('No')
            print('\n> Declined')

    with open(f'{LABELED}/{doc}', 'w') as d:
        d.write(lines)
    with open(f'{LABELS}/{doc}', 'w') as d:
        d.write('\n'.join(labels))


def main():
    labeled = {os.path.basename(f) for f in find_files(f'{LABELED}/*.txt')}
    not_labeled = {os.path.basename(f) for f in find_files(f'{NOT_LABELED}/*.txt')}

    list(map(process_paragraphs, not_labeled.difference(labeled)))
    return 0
    

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('EXIT')
        sys.exit(130)
