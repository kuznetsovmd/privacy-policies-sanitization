from functools import wraps
import glob
import os
import shutil


def remove_paths(paths):
    tuple(shutil.rmtree(p, ignore_errors=True) for p in paths)


def make_paths(paths):
    tuple(os.makedirs(p, exist_ok=True) for p in paths)


def list_files(path): 
    return set(glob.glob(path, include_hidden=True))


def read_lines(filename):
    return open(filename, encoding='utf-8').read().strip()
