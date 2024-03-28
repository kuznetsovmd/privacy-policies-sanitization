

import argparse
import sys

from datasets.config import filtering_conf, sanitization_conf
from datasets.filtering import make_filter_dataset
from datasets.sanitization import make_sanitizer_dataset
from env import env
from filtering.config import filter_evaluation_conf, filter_training_conf
from filtering.filter import eval_filter, train_filter
from finalization.finalize import finalize
from finalization.config import finalizer_conf
from sanitization.config import sanitizer_evaluation_conf, sanitizer_training_conf
from sanitization.sanitize import eval_sanitizer, train_sanitizer


def main(args):
    if args.cmd == 'make-dataset':
        if args.filtering:
            make_filter_dataset(**filtering_conf(**env()))
        if args.sanitization:
            make_sanitizer_dataset(**sanitization_conf(**env()))
    if args.cmd == 'filter':
        if args.train:
            train_filter(**filter_training_conf(**env()))
        if args.eval:
            eval_filter(**filter_evaluation_conf(**env()))
    if args.cmd == 'sanitize':
        if args.train:
            train_sanitizer(**sanitizer_training_conf(**env()))
        if args.eval:
            eval_sanitizer(**sanitizer_evaluation_conf(**env()))
    if args.cmd == 'ner':
        ...
    if args.cmd == 'finalize':
        finalize(**finalizer_conf(**env()))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='privacy-sanitization',
        description='Command line tool to control sanitization framework'
    )

    parser.add_argument('cmd', help='One of: make-dataset, filter, sanitize, ner, finalize')
    parser.add_argument('-f', '--filtering', default=False, action='store_true', help='for make-dataset')
    parser.add_argument('-s', '--sanitization', default=False, action='store_true', help='for make-dataset')
    parser.add_argument('-t', '--train', default=False, action='store_true', help='for filter & sanitize')
    parser.add_argument('-e', '--eval', default=False, action='store_true', help='for filter & sanitize')
    args = parser.parse_args()

    try:
        sys.exit(main(args))
    except KeyboardInterrupt:
        print('Interrupted by user')
        sys.exit(130)
    # except Exception as e:
        # print(e)
        # sys.exit(1)
