import argparse
import sys

from env import env
from descriptor_generation.config import conf as desc_conf
from descriptor_generation.main import main as make_descriptor
from html_sanitization.config import conf as html_conf
from html_sanitization.main import main as html_sanitization
from ner_custom.main import main as custom_ner_remove
from ner_custom.config import conf as custom_ner_conf
from ner_deeppavlov.main import main as deeppavlov_ner
from ner_deeppavlov.config import conf as deeppavlov_conf
from ner_natasha.main import main as natasha_ner
from ner_natasha.config import conf as natasha_conf
from ner_stanza.main import main as stanza_ner
from ner_stanza.config import conf as stanza_conf
from ner_spacy.main import main as spacy_ner
from ner_spacy.config import conf as spacy_conf
from ner_transformers.main import main as transformers_ner
from ner_transformers.config import conf as transformers_conf


def main(args):
    if args.cmd == 'gen-descriptor':
        make_descriptor(**desc_conf(**env()))
    if args.cmd == 'sanitize-html':
        html_sanitization(**html_conf(**env()))
    if args.cmd == 'remove-ne':
        custom_ner_remove(**custom_ner_conf(**env()))
    if args.cmd == 'deeppavlov-ne':
        deeppavlov_ner(**deeppavlov_conf(**env()))
    if args.cmd == 'natasha-ne':
        natasha_ner(**natasha_conf(**env()))
    if args.cmd == 'stanza-ne':
        stanza_ner(**stanza_conf(**env()))
    if args.cmd == 'spacy-ne':
        spacy_ner(**spacy_conf(**env()))
    if args.cmd == 'transformers-ne':
        transformers_ner(**transformers_conf(**env()))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='privacy-sanitization',
        description='Command line tool to control sanitization framework'
    )

    parser.add_argument(
        'cmd', 
        choices=['sanitize-html', 'remove-ne', 'deeppavlov-ne', 'natasha-ne', 
                 'stanza-ne', 'spacy-ne', 'transformers-ne', 'gen-descriptor'])
    args = parser.parse_args()

    try:
        sys.exit(main(args))
    except KeyboardInterrupt:
        print('Interrupted by user')
        sys.exit(130)
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)
