from copy import copy
import re


def compile(regex):
    return {**regex, 'compiled': re.compile(regex['expr'], **regex['args'])}


def regex_match(regex, text):
    it = regex['compiled'].finditer(text)
    return [extract(i, regex['groups']) for i in it]


def regex_sub(regex, text):
    modified_string = copy(text)
    matches = []
    for match in regex_match(regex, modified_string):
        match['sub'] = regex['sub']
        matches.append(match)
    return replace_matches(modified_string, matches)


def extract(match, groups):
    if not groups:
        return {}
    gs = tuple(match.group(g) for g in groups)
    ss = tuple(match.start(g) for g in groups)
    es = tuple(match.end(g) for g in groups)
    return {
        'groups': tuple(g for g in gs if g),
        'coords': (min(s for s in ss if s >= 0), 
                   max(e for e in es if e >= 0))
    }


def default_criterion(item):
    s, e = item['coords']
    return (s, s - e)


def merge_matches(items, criterion):
    if not items:
        return items
    items = sorted(items, key=criterion)
    items = ({**i, 'groups': (i['groups'],)} for i in items)
    merged = [next(items)]
    for i in items:
        cg = merged[-1]['groups']
        cc = merged[-1]['coords']
        cs, ce = cc
        s, e =  i['coords']
        g = i['groups']
        if cs <= s and e <= ce :
            continue
        if ce >= s and e > ce:
            merged[-1]['groups'] = (*cg, *g)
            merged[-1]['coords'] = (cs, e)
            continue
        merged.append(i)
    return merged


def replace_matches(text, items):
    if not items:
        return text
    tmp, p = '', 0
    for c in items:
        s, e, sub, gs = *c['coords'], c['sub'], c['groups']
        tmp, p = f'{tmp}{text[p:s]}{sub(gs)}', e
    return f'{tmp}{text[p:]}'