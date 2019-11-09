import re

def ltmd2latex(s:str) -> str:
    r"""
    input will like:(or something else)
    |   $1+1=$
    |   -------------------------
    |   - $2$
    |   - $\lim_{x\to 0} f(x)=x$
    |   - maybe 4
    |   - there is no corrent anwser
    and then output will be:
    |   $1+1=$
    |   \hspace*{\fill}\mbox{(~~~~~~~~~~)}
    |   \begin{enumerate}[A.]
    |       \item $2$
    |       \item $\lim_{x\to 0} f(x)=x$
    |       \item maybe 4
    |       \item there is no corrent anwser
    |   \end{enumerate}
    """
    str_begin_with_sym_sub = r'-+[^-\s]+|-+[^-]+.+'
    str_begin_without_sym_sub = r'[^-].*'
    # <str> ::= <str_begin_with_sym_sub> (<newline> <str>)*
    #        |  <str_begin_without_sym_sub> (<newline> <str>)*
    #        |  <item_begin> (<newline> <str>)*
    # <title> ::= <str>

    line = r'-+\s*'

    item_begin = r'-\s.*'
    # <item> ::= <item_brgin> <newline> <str>
    #         |  <item_begin>
    # <items> ::= <item> <items>

    spaceline = r'\s*'

    # <valid> ::= <title>
    #          |  <title> <newline> <line>
    #          |  <title> <newline> <line> <items>
    #          |  <title> <newline> <items>

    def ltmd2token(s:str) -> list:
        """
        this is a sub function of ltmd2latex
        """
        result_list = []
        for i in s.split('\n'):
            if re.fullmatch(line, i):
                result_list.append(('line', i))
            elif re.fullmatch(item_begin, i):
                result_list.append(('item_begin', i))
            elif re.fullmatch(str_begin_with_sym_sub, i):
                result_list.append(('str_begin_with_sym_sub', i))
            elif re.fullmatch(str_begin_without_sym_sub, i):
                result_list.append(('str_begin_without_sym_sub', i))
            elif re.fullmatch(spaceline, i):
                result_list.append(('spaceline', i))
            else:
                result_list.append(('invaild', i))
        return result_list

    tree_dict = {
        'str': [['item_begin', 'str'],
                ['str_begin_with_sym_sub', 'str'],
                ['str_begin_without_sym_sub', 'str'],
                ['item_begin'],
                ['str_begin_with_sym_sub'],
                ['str_begin_without_sym_sub']],
        'title': [['str']],
        'item': [['item_begin', 'str'],
                 ['item_begin']],
        'items': [['item', 'items'],
                  ['item']],
        'valid': [['title', 'line', 'items'],
                  ['title', 'line'],
                  ['title', 'items'],
                  ['title']],
        'spacelines': [['spaceline', 'spacelines'],
                       ['spaceline']],
        'tree': [['spacelines', 'valid', 'spacelines', 'tree'],
                 ['spacelines', 'valid', 'tree'],
                 ['valid', 'spacelines', 'tree'],
                 ['valid', 'tree'],
                 ['spacelines', 'valid', 'spacelines'],
                 ['spacelines', 'valid'],
                 ['valid', 'spacelines'],
                 ['valid'],]
    }

    def token2tree(l:list) -> list:
        """
        this is a sub function of ltmd2latex

        the output will look like:
        0: ('valid', 1, 6, 7)
        1: ('title', 2)
        2: ('str', 3, 4)
        3: ('str_begin_without_sym_sub', 'what is your anwser?')
        4: ('str', 5)
        5: ('item_begin', '- what you can do is tell me truth')
        6: ('line', '----------------------')
        7: ...
        """
        info_index = 0
        tree_list = ['tree']
        def get_tree_by_info(info: str) -> None:
            if type(tree_list[-1]) == str:
                for i in tree_dict[tree_list[-1]]:
                    if info in 
        for i in l:
            i_info = i[info_index]
            get_tree_by_info(i_info)

    return ltmd2token(s)

print(ltmd2latex("""balabala
how about this?
--------------------------
- a
- b
- c
- d
"""))
