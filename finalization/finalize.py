import os
import shutil
from finalization.filter_length import filter_length
from finalization.ruled_format import ruled_format
from finalization.integrate import make_descriptor
from utils.fsys import list_files


def finalize(input_files, old_descriptor, new_descriptor, output_files):
    files = list_files(input_files)

    for f in files:
        shutil.copyfile(f, f'{output_files}/{os.path.basename(f)}')

    filter_length(output_files)
    ruled_format(output_files)
    make_descriptor(output_files, old_descriptor, new_descriptor)
