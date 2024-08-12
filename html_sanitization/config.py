import re
import json
import nltk

from nltk.corpus import stopwords
from bs4 import Comment, NavigableString, Tag
from html_sanitization.counters import structure_elements, text_elements
from html_sanitization.decorate import decorate_h1, decorate_h2, decorate_h3, decorate_h4, decorate_h5, decorate_h6, decorate_li, decorate_table
from html_sanitization.functions import document_regex, element_regex, extract_strings, get_attribute_value, process_element, remove_element, unwrap_element, wrap_strings
from utils.regexes import compile
from utils.fsys import make_paths, read_lines, remove_paths


def conf(resources, tqdm_conf, **kwargs):
    with open(f'{resources}/frequent.json', 'r') as s:
        frequent_words = json.load(s)

    nltk.download('stopwords')
    russian_stopwords = stopwords.words('russian')
    russian_stopwords.extend(read_lines(f'{resources}/stopwords.txt').split('\n'))

    inputs = {
        'input_files': f'/mnt/Source/kuznetsovmd/datasets/ppr-dataset/original_policies/*.*',
        'stats_file': f'{resources}/statistics.json',
        'legacy_stats_file': f'{resources}/legacy_statistics.json',
        'stopwords': russian_stopwords,
        'frequent_words': frequent_words,
        'words_cnt': 100,
        'cpu_count': 12,
        'grams_n': 5,
        'short_threshold': 1000,
        'uppercase_threshold': .1,
        'foreign_threshold': .25,
        'frequent_threshold': 2.5,
        'deprecated_rules': [
            lambda x: '.pdf' in x, 
            lambda x: '.doc' in x, 
        ],
        'sanitizer_conf': {
            'local_functions': [
                process_element(lambda e: isinstance(e, Comment), remove_element),
                process_element(lambda e: isinstance(e, Tag) and e.name in {
                    'span', 'b','strong','i','em', 's', 'u', 'strike', 'mark', 'center', 'small', 'del', 'ins','sub','sup', 'nobr', 'font', 'mark', 'q', 'blockquote'
                }, unwrap_element),
                process_element(lambda e: isinstance(e, Tag) and e.name not in {
                    'div', 'p', 'ol', 'ul', 'li', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'tr', 'th', 'td', 'caption', 'colgroup', 'thead', 'tfoot', 'tbody',  'main', 'article', 'section', 'br', 'pre'
                }, remove_element),
                process_element(lambda e: isinstance(e, Tag) and any(c in ' '.join(get_attribute_value(e, 'class')).lower() for c in {
                    'head', 'cart', 'foot', 'nav', 'bar', 'alert', 'modal', 'order','maintenance', 'banner', 'promo', 'side', 'notif', 'tool', 'menu',  'ft', 'hd', 'shop', 'footer', 'ftr', 'address', 'adr', 'feedback', 'top', 'select', 'option', 'button', 'tip', 'call', 'phone', 'header', 'side', 'btn', 'input', 'textarea', 'dropdown', 'title', 'combo', 'warning', 'popup', 'icon', 'mobile', 'logo', 'basket', 'contacts', 'iframe', 'frame', 'captcha', 'price', 'count', 'plus', 'minus', 'faq', 'scroll', 'cover', 'bot', 'close', 'staff', 'catalog', 'products', 'favs', 'viewed', 'favourit', 'sale', 'benefit', 'copyright', 'breadcrumb', 'review', 'slide', 'carousel', 'filter', 'path', 'url', 'submenu', 'adsense', 'yandex', 'google', 'ads', 'hidden', 'radio', 'submit', 'checkbox', 'skip', 'social', 'search', 'testimonials', 'search', 'right', 'left', 'bot', 'baner'
                }), remove_element),
                process_element(lambda e: isinstance(e, Tag) and any(c in get_attribute_value(e, 'id').lower() for c in {
                    'head', 'cart', 'foot', 'nav', 'bar', 'alert', 'modal', 'order','maintenance', 'banner', 'promo', 'side', 'notif', 'tool', 'menu',  'ft', 'hd', 'footer', 'ftr', 'address', 'adr', 'feedback', 'top', 'select', 'option', 'button', 'tip', 'call', 'phone', 'header', 'side', 'btn', 'input', 'textarea', 'dropdown', 'title', 'combo', 'warning', 'popup', 'icon', 'mobile', 'logo', 'basket', 'contacts', 'iframe', 'frame', 'captcha', 'price', 'count', 'plus', 'minus', 'faq', 'scroll', 'cover', 'bot', 'close', 'staff', 'catalog', 'products', 'favs', 'viewed', 'favourit', 'sale', 'benefit', 'copyright', 'breadcrumb', 'review', 'slide', 'carousel', 'filter', 'path', 'url', 'submenu', 'yandex', 'google', 'ads', 'hidden', 'radio', 'submit', 'checkbox', 'skip', 'social', 'search', 'testimonials', 'search', 'right', 'left', 'bot', 'baner'
                }), remove_element),
                process_element(lambda e: isinstance(e, Tag) and any(c in get_attribute_value(e, 'role').lower() for c in {
                    'head', 'cart', 'foot', 'nav', 'bar', 'alert', 'modal', 'order','maintenance', 'banner', 'promo', 'side', 'notif', 'tool', 'menu',  'ft', 'hd', 'footer', 'ftr', 'address', 'adr', 'feedback', 'top', 'select', 'option', 'button', 'tip', 'call', 'phone', 'header', 'side', 'btn', 'input', 'textarea', 'dropdown', 'title', 'combo', 'warning', 'popup', 'icon', 'mobile', 'logo', 'basket', 'contacts', 'iframe', 'frame', 'captcha', 'price', 'count', 'plus', 'minus', 'faq', 'scroll', 'cover', 'bot', 'close', 'staff', 'catalog', 'products', 'favs', 'viewed', 'favourit', 'sale', 'benefit', 'copyright', 'breadcrumb', 'review', 'slide', 'carousel', 'filter', 'path', 'url', 'submenu', 'yandex', 'google', 'ads', 'hidden', 'radio', 'submit', 'checkbox', 'skip', 'social', 'search', 'testimonials', 'search', 'right', 'left', 'bot', 'baner'
                }), remove_element),
                process_element(lambda e: isinstance(e, Tag) and any(c in get_attribute_value(e, 'type').lower() for c in {
                    'head', 'cart', 'foot', 'nav', 'bar', 'alert', 'modal', 'order','maintenance', 'banner', 'promo', 'side', 'notif', 'tool', 'menu',  'ft', 'hd', 'footer', 'ftr', 'address', 'adr', 'feedback', 'top', 'select', 'option', 'button', 'tip', 'call', 'phone', 'header', 'side', 'btn', 'input', 'textarea', 'dropdown', 'title', 'combo', 'warning', 'popup', 'icon', 'mobile', 'logo', 'basket', 'contacts', 'iframe', 'frame', 'captcha', 'price', 'count', 'plus', 'minus', 'faq', 'scroll', 'cover', 'bot', 'close', 'staff', 'catalog', 'products', 'favs', 'viewed', 'favourit', 'sale', 'benefit', 'copyright', 'breadcrumb', 'review', 'slide', 'carousel', 'filter', 'path', 'url', 'submenu', 'yandex', 'google', 'ads', 'hidden', 'radio', 'submit', 'checkbox', 'skip', 'social', 'search', 'testimonials', 'search', 'right', 'left', 'bot', 'baner'
                }), remove_element),
                process_element(lambda e: isinstance(e, Tag) and any(c in get_attribute_value(e, 'style').lower().replace(' ', '') for c in {
                    'display:none', 'position:absolute'
                }), remove_element),
                process_element(lambda e: isinstance(e, Tag) and 'true' == get_attribute_value(e, 'area-hidden').lower(), remove_element),
                process_element(lambda e: isinstance(e, Tag) and 'true' == get_attribute_value(e, 'hidden').lower(), remove_element),

                process_element(lambda e: isinstance(e, NavigableString), element_regex(compile({
                    'sub': lambda _: '', 
                    'args': {},
                    'expr': r'\u00ad|&#183;|&nbsp;|&#160;|&#xa0;|&#10;|&#xa;|&#13;|&nbsp;|&#xd;',
                    'groups': (0,),
                }))),
                process_element(lambda e: isinstance(e, NavigableString), element_regex(compile({
                    'sub': lambda _: '-', 
                    'args': {},
                    'expr': r'[—–]',
                    'groups': (0,),
                }))), 
                process_element(lambda e: isinstance(e, NavigableString), element_regex(compile({
                    'sub': lambda _: ' ', 
                    'args': {},
                    'expr': r'[^А-ЯЁа-яёA-Za-z0-9.,:;\\\/\-\n\(\)\{\}\[\]*?!@#=+\^%$_ ]+',
                    'groups': (0,),
                }))),
                
                process_element(lambda e: isinstance(e, NavigableString) and e.parent.name != 'pre', wrap_strings),
                process_element(lambda e: isinstance(e, Tag) and not e.text.strip() and e.name != 'br', remove_element),
                process_element(lambda e: isinstance(e, NavigableString) and not e.text.strip(), remove_element),

                process_element(lambda e: isinstance(e, NavigableString), element_regex(compile({
                    'sub': lambda g: f'\\{g[0]}', 
                    'args': {'flags': re.MULTILINE},
                    'expr': r'(?!^[*_])(\*|\_)',
                    'groups': (0,),
                }))),
                process_element(lambda e: isinstance(e, NavigableString), element_regex(compile({
                    'sub': lambda _: ' ', 
                    'args': {},
                    'expr': r' {2,}',
                    'groups': (0,),
                }))),
                process_element(lambda e: isinstance(e, NavigableString), element_regex(compile({
                    'sub': lambda _: '', 
                    'args': {'flags': re.MULTILINE},
                    'expr': r'^ +',
                    'groups': (0,),
                }))),
                
                process_element(lambda e: isinstance(e, NavigableString), decorate_h1),
                process_element(lambda e: isinstance(e, NavigableString), decorate_h2),
                process_element(lambda e: isinstance(e, NavigableString), decorate_h3),
                process_element(lambda e: isinstance(e, NavigableString), decorate_h4),
                process_element(lambda e: isinstance(e, NavigableString), decorate_h5),
                process_element(lambda e: isinstance(e, NavigableString), decorate_h6),

                process_element(lambda e: isinstance(e, NavigableString), element_regex(compile({
                    'sub': lambda _: r'\.', 
                    'args': {'flags': re.MULTILINE},
                    'expr': r'^(\.)',
                    'groups': (1,),
                }))),
                process_element(lambda e: isinstance(e, NavigableString), element_regex(compile({
                    'sub': lambda _: r'\.', 
                    'args': {'flags': re.MULTILINE},
                    'expr': r'^\d{1,2}(\.)',
                    'groups': (1,),
                }))),

                process_element(lambda e: isinstance(e, NavigableString), decorate_li),
                # process_element(lambda e: isinstance(e, Tag) and e.name == 'table', decorate_table),
            ],

            'count_functions': [structure_elements, text_elements],
            'extract_function': extract_strings,

            'global_functions': [
                document_regex(compile({
                    'sub': lambda _: '', 
                    'args': {'flags': re.MULTILINE},
                    'expr': r'^[^А-ЯЁа-яёA-Za-z]+$',
                    'groups': (0,),
                })),
                document_regex(compile({
                    'sub': lambda _: '', 
                    'args': {},
                    'expr': r'[\dА-ЯЁа-яёA-Za-z]( +)[.,:;\\\/\)\}\]?!@]',
                    'groups': (1,),
                })),
                document_regex(compile({
                    'sub': lambda _: '', 
                    'args': {},
                    'expr': r'[\\\/\(\{\[@]( +)[\dА-ЯЁа-яёA-Za-z]',
                    'groups': (1,),
                })),
                document_regex(compile({
                    'sub': lambda _: '\n\n',
                    'args': {},
                    'expr': r'\n{3,}',
                    'groups': (0,),
                })),
            ]
        },
        'tqdm_conf': tqdm_conf,
    }

    outputs = {
        'sanitized_files': f'{resources}/sanitized_html',
    }
    remove_paths(outputs.values())
    make_paths(outputs.values())

    return { **inputs, **outputs }
