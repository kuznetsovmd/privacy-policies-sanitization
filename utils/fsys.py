from functools import wraps
import glob
import os


def make_paths(paths):
    [os.makedirs(p, exist_ok=True) for p in paths]


def list_files(path): 
    return glob.glob(path)


def read_lines(filename):
    return open(filename, encoding='utf-8').read().strip()
