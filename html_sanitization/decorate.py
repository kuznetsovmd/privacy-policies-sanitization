from bs4 import NavigableString, Tag


def get_path(element):
    ce, ep = element, []
    while ce.parent:
        ep.append(ce.name)
        ce = ce.parent
    return ep


def decorate_table(element):
    table = Tag(name='table')
    for i, row in enumerate(element.find_all('tr'), start=1):
        tr = Tag(name='tr')
        for j, col in enumerate(row.find_all('th'), start=1):
            if not col.text.strip():
                continue
            
            th = Tag(name='th')
            th.append(NavigableString(f'***Таблица (заголовок, строка {i}, столбец {j})***'))

            p = Tag(name='p')
            p.extend(col.extract().contents)
            th.append(p)
            tr.append(th)

        for j, col in enumerate(row.find_all('td'), start=1):
            if not col.text.strip():
                continue
            
            td = Tag(name='td')
            td.append(NavigableString(f'***Таблица (строка {i}, столбец {j})***'))

            p = Tag(name='p')
            p.extend(col.extract().contents)
            td.append(p)
            tr.append(td)
        
        table.append(tr)

    element.replace_with(table)


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
    if'h1' in get_path(element) and text:
        h1 = Tag(name='h1')
        h1.append(NavigableString(f'# {text}'))
        element.replace_with(h1)


def decorate_h2(element):
    text = element.text.strip()
    if'h2' in get_path(element) and text:
        h2 = Tag(name='h2')
        h2.append(NavigableString(f'## {text}'))
        element.replace_with(h2)


def decorate_h3(element):
    text = element.text.strip()
    if'h3' in get_path(element) and text:
        h3 = Tag(name='h3')
        h3.append(NavigableString(f'### {text}'))
        element.replace_with(h3)


def decorate_h4(element):
    text = element.text.strip()
    if'h4' in get_path(element) and text:
        h4 = Tag(name='h4')
        h4.append(NavigableString(f'#### {text}'))
        element.replace_with(h4)


def decorate_h5(element):
    text = element.text.strip()
    if'h5' in get_path(element) and text:
        h5 = Tag(name='h5')
        h5.append(NavigableString(f'##### {text}'))
        element.replace_with(h5)


def decorate_h6(element):
    text = element.text.strip()
    if'h6' in get_path(element) and text:
        h6 = Tag(name='h6')
        h6.append(NavigableString(f'###### {text}'))
        element.replace_with(h6)
