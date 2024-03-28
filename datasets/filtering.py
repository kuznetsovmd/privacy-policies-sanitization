import os
import shutil

from datasets.cli import ask, policy_head
from utils.fsys import list_files


def process_document(editor, input_doc, output_true, output_false):
    policy_head(os.path.basename(input_doc))
    
    os.system(f'{editor} {input_doc}')

    a = ask(
        '> Do you want to accept this document? y/n', 
        {'y': '\n> Accepted', 'n': '\n> Declined'},
        {'y': True, 'n': False})
    
    if a:
        shutil.copyfile(input_doc, output_true)
    elif not a:
        shutil.copyfile(input_doc, output_false)


def make_filter_dataset(editor, input_docs, output_true, output_false):
    not_labeled = {os.path.basename(f) for f in list_files(f'{input_docs}/*.txt')}
    seen_true = {os.path.basename(f) for f in list_files(f'{output_true}/*.txt')}
    seen_false = {os.path.basename(f) for f in list_files(f'{output_false}/*.txt')}

    unseen = not_labeled.difference(seen_true | seen_false)
    editors = [editor for _ in unseen]
    inputs = sorted(f'{input_docs}/{os.path.basename(i)}' for i in unseen)
    outputs_true = sorted(f'{output_true}/{os.path.basename(i)}' for i in inputs)
    outputs_false = sorted(f'{output_false}/{os.path.basename(i)}' for i in inputs)

    list(map(process_document, editors, inputs, outputs_true, outputs_false))
