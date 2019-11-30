import colored

def print_256_color():
    print(' '*9, *['{:<7}'.format(i) for i in range(10)], sep='')
    for i in range(0, 256, 10):
        print(f' {i:5} >', end='')
        for j in range(10):
            try:
                print(f'{colored.fg(i+j)} {"("+str(i+j)+")":-^5} {colored.attr(0)}', end='')
            except KeyError:
                break
        print()
        
# -------------------------------------------------------------------------------------------
token_color = '#888888'
important_color = '#ffaaaa'

def c(text, color):
    # meaning: color
    return colored.fg(color) + text + colored.attr(0)

def tok(token):
    # meaning: token
    return c(token, token_color)

# meaning: quote token
tok_q = tok('"')

def imp(important_text):
    # meaning: important
    return c(important_text, important_color)