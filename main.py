import argparse
import sys

from datasets.config import dataset_conf
from datasets.make_dataset import make_dataset
from html_sanitization.config import html_conf
from html_sanitization.sanitization import sanitize_html
from env import env
from ner_custom.custom_ner import ner_remove as custom_ner_remove
from ner_custom.config import ner_conf as custom_ner_conf
from deep_sanitization.config import \
    sanitizer_training_conf as onelayer_training_conf, \
    sanitizer_evaluation_conf as onelayer_evaluation_conf
from deep_sanitization.sanitization import \
    train_sanitizer as train_onelayer_sanitizer, \
    eval_sanitizer as eval_onelayer_sanitizer


def main(args):
    if args.cmd == 'sanitize-html':
        sanitize_html(**html_conf(**env()))

    if args.cmd == 'sanitize-deep':
        if args.train:
            train_onelayer_sanitizer(**onelayer_training_conf(**env()))
        if args.eval:
            eval_onelayer_sanitizer(**onelayer_evaluation_conf(**env()))

    if args.cmd == 'make-dataset':
        make_dataset(**dataset_conf(**env()))

    if args.cmd == 'remove-ne':
        custom_ner_remove(**custom_ner_conf(**env()))

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='privacy-sanitization',
        description='Command line tool to control sanitization framework'
    )

    parser.add_argument('cmd', help='One of: sanitize-html, sanitize-deep, make-dataset, remove-ne')
    parser.add_argument('-t', '--train', default=False, action='store_true', help='for legacy-filter & legacy-sanitize & sanitize')
    parser.add_argument('-e', '--eval', default=False, action='store_true', help='for legacy-filter & legacy-sanitize & sanitize')
    args = parser.parse_args()

    try:
        sys.exit(main(args))
    except KeyboardInterrupt:
        print('Interrupted by user')
        sys.exit(130)
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)
