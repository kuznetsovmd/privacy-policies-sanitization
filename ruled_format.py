import sys
import os
import re

from docs import *


dates_regex = re.compile(r'(\d{2})\. (\d{2})\. (\d{2,})')
tel_regex = re.compile(r'(\+?7|8)\s*[-(]?\d{3}[)-]?[\s-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}\s*(доб\. \d{1,2})?')
chapters_regex = re.compile(r'( [а-яa-zА-ЯA-Z)]+(?<!...\sш|.\sком|..\sвл|...\sд|...\sч|.\sстр|..\sст|.\sпом|.\sмаг|..\sул|...\sк|.\sобл|..\sоф|.\sкор|..\sзд|..\sэт|..\sпп|...\sп|..\sкв|.\sкаб|..\sпр|...\sс|.\sпер|.\sпав|.\sнаб|\sкорп|.\sред|\sвлад|...\sг|.\sгор)\.?)\s((\d{1,2}\.\s)*\d{1,2}\.\s)', flags=re.MULTILINE | re.IGNORECASE)
websites_regex = re.compile(r'(\{removed href\}|\{removed hyperref\})?(\s*https?:?\/\/)?[0-9а-яa-zА-ЯA-Z_\-&]+\. (рф|php|html|онлайн)\s*(\{removed href\}|\{removed hyperref\})?', flags=re.IGNORECASE)
false_newlines_regex = re.compile(r'([а-яa-zА-ЯA-Z])\.\n{3}([а-яa-z])', flags=re.MULTILINE)
inn_regex = re.compile(r'ИНН\s*:?\s*\d{5,}')
ogrn_regex = re.compile(r'ОГРН?(\(?ИП\)?)?\s*:?\s*\d{5,}')
ip_regex = re.compile(r'ИП\s*:?\s*([А-Я]\.?\s*[А-Я]\.\s*[А-Я][а-яА-Я]+|[А-Я][а-яА-Я]+\s*[А-Я]\.?\s*[А-Я]\.|[А-Я][а-яА-Я\-]+\s*[А-Я][а-яА-Я\-]+\s*[А-Я][а-яА-Я\-]+)')

address_regex1 = re.compile(r'(^|\s)г\. ([А-Я][А-Яа-я\-]{3,}( Челны| Новгород)?)', flags=re.IGNORECASE)
address_regex2 = re.compile(r'([А-Я][А-Яа-я\-]{3,}( Челны)?) г\.')
county_regex1 = re.compile(r'[А-Я][А-Яа-я\-]{3,} (кра[йя]|обл?\.|област[ьи])')
county_regex2 = re.compile(r'[рР]еспублика [А-Я][А-Яа-я\-]{3,}( Эл)?')
steet_regex = re.compile(r'([А-Я][А-Яа-я]+([\s-][А-Я][А-Яа-я]+)?)\s+(улица |шоссе |ш\. |вл\. |ул\. |маг\. |[пП]рк?-к?т |[пП]роспект |[пП]роезд |[нН]абережная )|(улица|шоссе|ш\.|вл\.|ул\.|маг\.|[пП]рк?-к?т|[пП]роспект|[пП]роезд|[нН]абережная)\s+([А-Я][А-Яа-я]+([\s-][А-Я][А-Яа-я]+)?)')
post_regex = re.compile(r'\d{6}')

FILES = f'{RESOURCES}/filtered_policies/yes/'
FORMATTED = f'{RESOURCES}/formatted_policies/'


def process_paragraphs(doc):
    formatted = read_lines(f'{FILES}/{doc}')

    formatted = dates_regex.sub('\g<1>.\g<2>.\g<3>', formatted)
    formatted = websites_regex.sub('{removed href}', formatted)
    formatted = ogrn_regex.sub('{removed credentials}', formatted)
    formatted = inn_regex.sub('{removed credentials}', formatted)
    formatted = ip_regex.sub('{removed businessman}', formatted)
    formatted = tel_regex.sub('{removed phone number}', formatted)
    formatted = false_newlines_regex.sub('\g<1> \g<2>', formatted)
    formatted = chapters_regex.sub('\g<1>\n\n\n\g<2>', formatted)

    if r := county_regex1.search(formatted):
        formatted = county_regex1.sub('{removed county}', formatted)

    if r := county_regex2.search(formatted):
        formatted = county_regex2.sub('{removed county}', formatted)

    if r := address_regex1.search(formatted):
        formatted = address_regex1.sub('{removed city}', formatted)
    
    if r := address_regex2.search(formatted):
        formatted = address_regex2.sub('{removed city}', formatted)

    if r := steet_regex.search(formatted):
        formatted = steet_regex.sub('{removed street}', formatted)

    if r := post_regex.search(formatted):
        formatted = post_regex.sub('{removed post}', formatted)

    with open(f'{FORMATTED}/{doc}', 'w') as d:
        d.write(formatted)


def main():
    files = {os.path.basename(f) for f in find_files(f'{FILES}/*.txt')}

    list(map(process_paragraphs, files))
    return 0
    

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('EXIT')
        sys.exit(130)
