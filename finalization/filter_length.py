import os

from utils.fsys import list_files, read_lines


def filter_length(output_files):
    files = list_files(f'{output_files}/*.txt')

    for f in files:
        content = read_lines(f)

        if len(content) < 500:
            os.remove(f) 
