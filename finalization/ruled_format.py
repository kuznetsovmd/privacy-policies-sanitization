import os
import re

from utils.data import *
from utils.fsys import list_files, read_lines


chapters_regex = re.compile(r'( [а-яa-zА-ЯA-Z)]+(?<!...\sш|.\sком|..\sвл|...\sд'
                            r'|...\sч|.\sстр|..\sст|.\sпом|.\sмаг|..\sул|...\sк'
                            r'|.\sобл|..\sоф|.\sкор|..\sзд|..\sэт|..\sпп|...\sп'
                            r'|..\sкв|.\sкаб|..\sпр|...\sс|.\sпер|.\sпав|.\sнаб'
                            r'|\sкорп|.\sред|\sвлад|...\sг|.\sгор)\.?)\s((\d{1,'
                            r'2}\.\s)*\d{1,2}\.\s)', flags=re.MULTILINE | re.IGNORECASE)
websites_regex = re.compile(r'(\{removed href\}|\{removed hyperref\})?(\s*https'
                            r'?:?\/\/)?[0-9а-яa-zА-ЯA-Z_\-&]+\. (рф|php|html|он'
                            r'лайн)\s*(\{removed href\}|\{removed hyperref\})?', flags=re.IGNORECASE)
ip_regex = re.compile(r'ИП\s*:?\s*([А-Я]\.?\s*[А-Я]\.\s*[А-Я][а-яА-Я]+|[А-Я][а-'
                      r'яА-Я]+\s*[А-Я]\.?\s*[А-Я]\.|[А-Я][а-яА-Я\-]+\s*[А-Я][а-'
                      r'яА-Я\-]+\s*[А-Я][а-яА-Я\-]+)')
tel_regex = re.compile(r'(\+?7|8)\s*[-(]?\d{3}[)-]?[\s-]*\d{3}[\s-]*\d{2}[\s-]*'
                       r'\d{2}\s*(доб\. \d{1,2})?')
false_newlines_regex = re.compile(r'([а-яa-zА-ЯA-Z])\.\n{3}([а-яa-z])', flags=re.MULTILINE)
dates_regex = re.compile(r'(\d{2})\. (\d{2})\. (\d{2,})')
ogrn_regex = re.compile(r'ОГРН?(\(?ИП\)?)?\s*:?\s*\d{5,}')
inn_regex = re.compile(r'ИНН\s*:?\s*\d{5,}')
post_regex = re.compile(r'\d{6}')


def ruled_format(output_files):
    files = {os.path.basename(f) for f in list_files(f'{output_files}/*.txt')}

    for f in files:
        formatted = read_lines(f'{output_files}/{f}')

        formatted = dates_regex.sub('\g<1>.\g<2>.\g<3>', formatted)
        formatted = websites_regex.sub('{removed href}', formatted)
        formatted = ogrn_regex.sub('{removed credentials}', formatted)
        formatted = inn_regex.sub('{removed credentials}', formatted)
        formatted = ip_regex.sub('{removed businessman}', formatted)
        formatted = tel_regex.sub('{removed phone number}', formatted)
        formatted = false_newlines_regex.sub('\g<1> \g<2>', formatted)
        formatted = chapters_regex.sub('\g<1>\n\n\n\g<2>', formatted)

        if post_regex.search(formatted):
            formatted = post_regex.sub('{removed post}', formatted)

        with open(f'{output_files}/{f}', 'w') as d:
            d.write(formatted)
