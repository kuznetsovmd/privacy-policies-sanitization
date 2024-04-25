

def gen_names_midnames(variants, long_sep, short_sep):
    return {
        'high': {f'{v.upper()}{s}' for v in variants for s in long_sep},
        'low': {f'{v.capitalize()}{s}' for v in variants for s in long_sep},
        'short': {f'{v[0].upper()}{s}' for v in variants for s in short_sep},
    }


def gen_surnames(variants, sep):
    return {
        'high': { f'{v.upper()}{s}' for v in variants for s in sep},
        'low': { f'{v.capitalize()}{s}' for v in variants for s in sep},
        'short': {*{f'{v.upper()}{s}' for v in variants for s in sep}, 
                  *{f'{v.capitalize()}{s}' for v in variants for s in sep}},
    }


def generate(names, midnames, surnames, short_sep, long_sep, sep):
    names, midnames, surnames = \
        gen_names_midnames(names, long_sep, short_sep), \
        gen_names_midnames(midnames, long_sep, short_sep), \
        gen_surnames(surnames, sep)
    return set( 
        positioning.format(n, m, s)
        for positioning in [' {0}{1}{2} ', ' {2}{0}{1} ']
        for shortening in ['high', 'low', 'short']
        for n in names[shortening]
        for m in midnames[shortening]
        for s in surnames[shortening]
    ])


if __name__ == '__main__':
    input = {
        'names': ['иван'],
        'midnames': ['иванович'],
        'surnames': ['иванов'],
        'long_sep':  [' ', ''],
        'short_sep': ['. ', ' ', ''],
        'sep':  [' ', ''],
    }

    print('\n'.join(sorted([f' {n} ' for n in generate(**input)])))
