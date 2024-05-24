from utils.regexes import compile, default_criterion


def dataset_regexes():
    EDGE = r'[^А-ЯЁа-яёA-Za-z]'
    EDGE_PLUS = r'[^А-ЯЁа-яёA-Za-z]+'
    DOS_REQ = r'[\.\s]+'
    DOS_OPT = r'[\.\s]*'
    SPC_REQ = r'\s+'
    SPC_OPT = r'\s*'
    NAME_SHORT = r'[А-ЯЁ]'
    NAME_UPPER = r'[А-ЯЁ]+'
    NAME_LOWER = r'[А-ЯЁ][а-яё]+'
    PREFIXES = [
        r'[Ии]\.?\s?[Пп]\.?:?',
        r'[Пп]редпринимател[а-яё]+:?',
        r'ПРЕДПРИНИМАТЕЛ[А-ЯЁ]+:?',
        r'[Бб]лог[а-яё]+:?'
        r'БЛОГ[А-ЯЁ]+:?'
        r'[Аа]администрац[а-яё]+ [Сс]айта:?'
        r'АДМИНИСТРАЦ[А-ЯЁ]+ САЙТА:?'
        r'РУКОВОДИТЕЛ[А-ЯЁ]+:?'
        r'[Рр]уководител[а-яё]+:?'
        r'[Мм]енеджер[а-яё]*:?'
        r'МЕНЕДЖЕР[А-ЯЁ]*:?'
        r'[Вв] [Лл]ице'
        r'В ЛИЦЕ',
        # r'принадлежащий на праве собственности/праве пользования '
        # r'действующие от имени'
        # r'Автор сайта'
        # r'Автор нашего проекта'
        # r'Индивидуальным предпринимателем'
    ]

    return tuple(map(compile, (
        {
            # 0 Все комбины для сокращений ловер фамилия первая
            'args': {},
            'expr': f'{EDGE}({"|".join(PREFIXES)}){EDGE_PLUS}'
                    f'({NAME_LOWER})({DOS_OPT}({NAME_SHORT}))?({DOS_OPT}({NAME_SHORT}))?{EDGE}',
            'groups': (2, 4, 6),
            'criterion': default_criterion
        }, {
            # 1 Все комбины для сокращений ловер имя первое
            'args': {},
            'expr': f'{EDGE}({"|".join(PREFIXES)}){EDGE_PLUS}'
                    f'(({NAME_SHORT}){DOS_OPT})?(({NAME_SHORT}){DOS_OPT})?({NAME_LOWER}){EDGE}',
            'groups': (3, 5, 6),
            'criterion': default_criterion
        }, {
            # 2 Все комбины для сокращений хаер фамилия первая
            'args': {},
            'expr': f'{EDGE}({"|".join(PREFIXES)}){EDGE_PLUS}'
                    f'({NAME_UPPER})({DOS_REQ}({NAME_SHORT}))?({DOS_REQ}({NAME_SHORT}))?{EDGE}',
            'groups': (2, 4, 6),
            'criterion': default_criterion
        }, {
            # 3 Все комбины для сокращений хаер имя первое
            'args': {},
            'expr': f'{EDGE}({"|".join(PREFIXES)}){EDGE_PLUS}'
                    f'(({NAME_SHORT}){DOS_REQ})?(({NAME_SHORT}){DOS_REQ})?({NAME_UPPER}){EDGE}',
            'groups': (3, 5, 6),
            'criterion': default_criterion
        }, {
            # 4 Все комбины для фула ловер
            'args': {},
            'expr': f'{EDGE}({"|".join(PREFIXES)}){EDGE_PLUS}'
                    f'(({NAME_LOWER}){SPC_OPT})?(({NAME_LOWER}){SPC_OPT})?({NAME_LOWER}){EDGE}',
            'groups': (3, 5, 6),
            'criterion': default_criterion
        }, {
            # 5 Все комбины для фула хаер
            'args': {},
            'expr': f'{EDGE}({"|".join(PREFIXES)}){EDGE_PLUS}'
                    f'({NAME_UPPER})({SPC_REQ}({NAME_UPPER}))?({SPC_REQ}({NAME_UPPER}))?{EDGE}',
            'groups': (2, 4, 6),
            'criterion': default_criterion
        }, 

        # {
        #     # 6 Все комбины для сокращений ловер фамилия первая (2 слова) Добавить разделителей
        #     'args': {},
        #     'expr': r'[^А-ЯЁа-яё]'
        #             r'([А-ЯЁ][а-яё]+)([\.\s]*([А-ЯЁ]))([\.\s]*([А-ЯЁ]))?[^А-ЯЁа-яё]',
        #     'groups': (1, 3, 5),
        #     'criterion': default_criterion
        # }, 
        # {
        #     # 7 Все комбины для сокращений ловер имя первое (2 слова) Добавить разделителей
        #     'args': {},
        #     'expr': r'[^А-ЯЁа-яё]'
        #             r'(([А-ЯЁ])[\.\s]*)?(([А-ЯЁ])[\.\s]*)([А-ЯЁ][а-яё]+)[^А-ЯЁа-яё]',
        #     'groups': (2, 4, 5),
        #     'criterion': default_criterion
        # },

        # {
        #     # 8 Все комбины для фула ловер
        #     'args': {'flags': re.MULTILINE},
        #     'expr': f'{EDGE}'
        #             f'(({NAME_LOWER})\s*)(({NAME_LOWER})\s*)({NAME_LOWER}){EDGE}',
        #     'groups': (2, 4, 5)
        # }, 

        # {
        #     # 9 Все комбины для сокращений хаер фамилия первая (3 слова) Добавить разделителей
        #     'args': {},
        #     'expr': r'[^А-ЯЁа-яё]'
        #             r'([А-ЯЁ]+)([\.\s]+([А-ЯЁ]))([\.\s]+([А-ЯЁ]))[^А-ЯЁа-яё]',
        #     'groups': lambda match: dict(
        #         groups=[match.group(1), match.group(3), match.group(5)],
        #         coords=[match.start(1), match.end(5)]
        # },  {
        #     # 10 Все комбины для сокращений хаер имя первое (3 слова) Добавить разделителей
        #     'args': {},
        #     'expr': r'[^А-ЯЁа-яё]'
        #             r'(([А-ЯЁ])[\.\s]+)(([А-ЯЁ])[\.\s]+)([А-ЯЁ]+)[^А-ЯЁа-яё]',
        #     'groups': lambda match: dict(
        #         groups=[match.group(2), match.group(4), match.group(5)],
        #         coords=[match.start(2), match.end(5)]
        # }, 
    )))


def names_regexes():
    EDGE = r'[^А-ЯЁа-яёA-Za-z]'
    DOS_REQ = r'[\.\s]+'
    DOS_OPT = r'[\.\s]*'
    NAME_SHORT = r'[А-ЯЁ]'
    NAME_UPPER = r'[А-ЯЁ]+'
    NAME_LOWER = r'[а-яё]+'

    return tuple(map(compile, (
        {
            # Полный вариант вариант ловер
            'sub': lambda _: '{potential subject}',
            'args': {},
            'expr': f'(?={EDGE}'
                    f'({NAME_SHORT}({NAME_LOWER})?){DOS_OPT}'
                    f'({NAME_SHORT}({NAME_LOWER})?){DOS_OPT}'
                    f'({NAME_SHORT}({NAME_LOWER})?){DOS_OPT}){EDGE}',
            'groups': (1, 3, 5),
            'criterion': default_criterion
        }, {
            # Упрощенный вариант ловер
            'sub': lambda _: '{potential subject}',
            'args': {},
            'expr': f'(?={EDGE}'
                    f'({NAME_SHORT}({NAME_LOWER})?){DOS_OPT}'
                    f'({NAME_SHORT}({NAME_LOWER})?){DOS_OPT}){EDGE}',
            'groups': (1, 3),
            'criterion': default_criterion
        }, {
            # Полный вариант вариант хаер
            'sub': lambda _: '{potential subject}',
            'args': {},
            'expr': f'(?={EDGE}'
                    f'({NAME_UPPER}){DOS_REQ}'
                    f'({NAME_UPPER}){DOS_REQ}'
                    f'({NAME_UPPER}){DOS_REQ}){EDGE}',
            'groups': (1, 2, 3),
            'criterion': default_criterion
        }, {
            # Упрощенный вариант хаер
            'sub': lambda _: '{potential subject}',
            'args': {},
            'expr': f'(?={EDGE}'
                    f'({NAME_UPPER}){DOS_REQ}'
                    f'({NAME_UPPER}){DOS_REQ}){EDGE}',
            'groups': (1, 2),
            'criterion': default_criterion
        }
    )))


def toponyms_regexes():
    return []
