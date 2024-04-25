from copy import copy
from bs4 import Comment, NavigableString, Tag

from utils.regexes import regex_sub


def get_attribute_keys(element):
    return element.attrs.keys()


def get_attribute_value(element, name):
    return element.attrs[name] if name in element.attrs else ''


def process_element(condition, action):
    def fn(element):
        if condition(element):
            action(element)
    return fn


def unwrap_element(element):
    element.unwrap()


def remove_element(element):
    if isinstance(element, Comment):
        element.extract()
    if isinstance(element, NavigableString):
        element.extract()
    if isinstance(element, Tag):
        for e in element.find_all(recursive=True):
            e.replace_with(' ')
        element.replace_with(' ')


def wrap_strings(element):
    p = Tag(name='p')
    element.insert_before(p)
    merged_string = []
    while isinstance(element, NavigableString):
        next_sibling = element.next_sibling
        merged_string.append(element.extract().text.replace('\n', ' '))
        element = next_sibling
    p.append(NavigableString(''.join(merged_string)))


def unwrap_table(element):
    items = []
    for i, row in enumerate(element.find_all('tr'), start=1):
        for j, col in enumerate((*row.find_all('th'), *row.find_all('td')), start=1):
            if not col.text.strip():
                continue
            
            p = Tag(name='p')
            p.append(NavigableString(f'***Таблица (строка {i}, столбец {j})***'))
            items.append(p)

            p = Tag(name='p')
            p.append(col.extract())
            items.append(p)

    table = Tag(name='p')
    table.extend(table)
    element.replace_with(table)


def element_regex(regex):
    def fn(element):
        element.replace_with(NavigableString(regex_sub(regex, element.text)))
    return fn


def document_regex(regex):
    def fn(text):
        return regex_sub(regex, text)
    return fn


def extract_strings(elements):
    strings = (e for e in elements if isinstance(e, NavigableString) and e.text.strip())
    return '\n\n'.join(s.text for s in strings)