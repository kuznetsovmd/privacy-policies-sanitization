import os
from getkey import getkey


def policy_head(entry, vfill=2, uped=2, dpad=2):
    size = os.get_terminal_size()
    upad_ = "\n"*uped
    dpad_ = "\n"*dpad
    vfill_ = "\n"*vfill
    print((f'{upad_}'
           f'{"#"*size.columns}\n'
           f'#{"POLICY".center(size.columns-2)}#\n'
           f'{"#"*size.columns}{vfill_}'
           f'>>> {entry}'
           f'{dpad_}'), end='')
    

def policy_paragraph(entry, order, text, vfill=2, uped=2, dpad=2):
    size = os.get_terminal_size() 
    upad_ = "\n"*uped
    dpad_ = "\n"*dpad
    vfill_ = "\n"*vfill
    print((f'{upad_}'
           f'{"#"*size.columns}{vfill_}'
           f'>>> policy {entry} '
           f'> paragraph {order}{vfill_}'
           f'{text}'
           f'{dpad_}'))


def ask(message, replies, outputs):
    print(message)
    while True:
        try:
            key = getkey()
            print(replies[key])
            return outputs[key]
        except KeyError:
            print('Wrong key!')
