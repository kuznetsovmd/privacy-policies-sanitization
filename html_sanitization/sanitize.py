import os

from bs4 import BeautifulSoup, NavigableString

from utils.fsys import read_lines


class Sanitize:
    def __init__(self, output_files, local_functions, extract_function, global_functions):
        Sanitize.output_files = output_files
        Sanitize.local_functions = local_functions
        Sanitize.extract_function = extract_function
        Sanitize.global_functions = global_functions
    
    @classmethod
    def __call__(cls, file):
        soup = BeautifulSoup(read_lines(file), 'html.parser')
        for fn in Sanitize.local_functions:
            Sanitize.__apply(soup, fn)

        text = Sanitize.extract_function(Sanitize.__list(soup.html))
        for fn in Sanitize.global_functions:
            text = fn(text)

        output_file = f'{cls.output_files}/{os.path.basename(file)}.md'
        with open(output_file, 'w') as f:
            f.write(text)

        return output_file

    @staticmethod
    def __apply(element, fn, ignore={'[document]', 'html', 'body'}):
        if not isinstance(element, NavigableString):
            for child in element.children:
                Sanitize.__apply(child, fn, ignore=ignore)
        if element.name not in ignore:
            fn(element)

    @staticmethod
    def __list(html):
        tree = [html]
        elements = []
        while tree:
            t = tree.pop()
            elements.append(t)
            if isinstance(t, NavigableString):
                continue
            tree.extend(reversed(list(c for c in t.children)))
        return elements