

import os
import shutil
import sys

from utils.fsys import list_files, make_paths, read_lines


def main():
    # FILTERING FALSE ALL FALSE
    # SANITIZATION DOCS + LABELS
    filtering_false = 'resources/filtering_false/*.txt'
    sanitization_docs = 'resources/sanitization_docs/*.txt'
    sanitization_labels = 'resources/sanitization_labels/*.txt'
    new_sanitization_docs = 'resources/onelayer_sanitization_docs'
    new_sanitization_labels = 'resources/onelayer_sanitization_labels'

    make_paths([new_sanitization_docs, new_sanitization_labels])
    
    files = list_files(filtering_false)
    for f in files:
        text = read_lines(f)
        paragraphs = len(text.split('\n\n\n'))

        shutil.copyfile(f, f'{new_sanitization_docs}/{os.path.basename(f)}')
        with open(f'{new_sanitization_labels}/{os.path.basename(f)}', 'w') as f_:
            f_.write('\n'.join(['No'] * paragraphs))

    files = list_files(sanitization_docs)
    for f in files:
        shutil.copyfile(f, f'{new_sanitization_docs}/{os.path.basename(f)}')

    files = list_files(sanitization_labels)
    for f in files:
        shutil.copyfile(f, f'{new_sanitization_labels}/{os.path.basename(f)}')
    

if __name__ == '__main__':
    sys.exit(main())
