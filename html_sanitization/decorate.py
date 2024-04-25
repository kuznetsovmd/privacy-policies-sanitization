from bs4 import NavigableString


def get_path(element):
    ce, ep = element, []
    while ce.parent:
        ep.append(ce.name)
        ce = ce.parent
    return ep


def decorate_li(element):
    ep, ce, s = [], element, 0
    while ce.parent:
        ep.append(ce.name)
        if not s and ce.name == 'ol' and 'start' in ce.attrs:
            s = ce.attrs["start"]
        ce = ce.parent

    p = list(reversed(ep)) 
    ol = p.index('ol') if 'ol' in p else len(p)
    ul = p.index('ul') if 'ul' in p else len(p)
    
    text = element.text.strip()
    if (li := p.count('li') - 1) >= 0 and text:
        indent = " " * 4 * li
        if ol < ul:
            element.replace_with(NavigableString(f'{indent}{s if s else 1}. {text}'))
        if ul < ol:
            element.replace_with(NavigableString(f'{indent}* {text}'))


def decorate_h1(element):
    text = element.text.strip()
    if 'h1' in get_path(element) and text:
        element.replace_with(NavigableString(f'# {text}'))


def decorate_h2(element):
    text = element.text.strip()
    if'h2' in get_path(element) and text:
        element.replace_with(NavigableString(f'## {text}'))


def decorate_h3(element):

    text = element.text.strip()
    if 'h3' in get_path(element) and text:
        element.replace_with(NavigableString(f'### {text}'))


def decorate_h4(element):
    text = element.text.strip()
    if'h4' in get_path(element) and text:
        element.replace_with(NavigableString(f'#### {text}'))


def decorate_h5(element):
    text = element.text.strip()
    if'h5' in get_path(element) and text:
        element.replace_with(NavigableString(f'##### {text}'))


def decorate_h6(element):
    text = element.text.strip()
    if'h6' in get_path(element) and text:
        element.replace_with(NavigableString(f'###### {text}'))
