import os
import shutil

from datasets.cli import ask, policy_head, policy_paragraph
from utils.fsys import list_files, read_lines


def process_paragraphs(input_doc, output_doc, output_labels):
    policy_head(os.path.basename(input_doc))

    labels = []
    for i, p in enumerate(read_lines(input_doc).split('\n\n')):
        policy_paragraph(os.path.basename(input_doc), i ,p)

        a = ask(
            '> Do you want to accept this paragraph? y/n', 
            {'y': '\n> Accepted', 'n': '\n> Declined'},
            {'y': True, 'n': False})
        
        if a:
            labels.append('Yes')
        elif not a:
            labels.append('No')

    shutil.copyfile(input_doc, output_doc)
    with open(output_labels, 'w') as d:
        d.write('\n'.join(labels))


def make_dataset(input_docs, output_docs, output_labels):
    not_labeled = {os.path.basename(f) for f in list_files(f'{input_docs}/*.txt')}
    labeled = {os.path.basename(f) for f in list_files(f'{output_docs}/*.txt')}

    unseen = not_labeled.difference(labeled)
    inputs = sorted(f'{input_docs}/{os.path.basename(i)}' for i in unseen)
    outputs = sorted(f'{output_docs}/{os.path.basename(i)}' for i in inputs)
    labels = sorted(f'{output_labels}/{os.path.basename(i)}' for i in inputs)

    list(map(process_paragraphs, inputs, outputs, labels))
