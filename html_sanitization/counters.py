
from bs4 import NavigableString, Tag


def structure_elements(element, stats):
    if isinstance(element, NavigableString):
        return stats
    if element.name not in {'table', 'tr', 'td', 'th', 'pre', 'ol', 'ul', 'li', 'section', 'article'}:
        return stats
    if element.name in stats:
        stats[element.name] += 1
    else:
        stats[element.name] = 1
    return stats


def text_elements(element, stats):
    if isinstance(element, NavigableString):
        return stats
    if element.name not in {'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'}:
        return stats
    if any(isinstance(c, Tag) and c.name == 'wrapped_string' for c in element.children):
        if element.name in stats:
            stats[element.name] += 1
        else:
            stats[element.name] = 1
    return stats
