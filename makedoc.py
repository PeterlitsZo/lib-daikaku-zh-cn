import re

def ltmd2latex(s:str) -> str:
    """
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
    # <str> ::= <str_begin_with_sym_sub> <newline> <title>
    #        |  <str_begin_without_sym_sub> <newline> <title>
    #        |  ...
    # <title> ::= <str>

    line = r'-+\s*'

    item_begin = r'-\s.*'
    # <item> ::= <item_brgin> <newline> <str>
    #         |  <item_begin>

    spaceline = r'\s*'

    # <valid> ::= <title>
    #          |  <title> <newline> <line>
    #          |  <title> <newline> <line> <item>+
    #          |  <title> <newline> <item>+

    def ltmd2token(s:str) -> list:
        """
        this is a sub function of ltmd2latex
        """
        result_list = []
        for i in s.split('\n'):
            if re.fullmatch(line, i)
                result_list.append(('line', i))
            elif re.fullmatch(str_begin_with_sym_sub, i):
                result_list.append(('str_begin_with_sym_sub', i))
            elif re.fullmatch(str_begin_without_sym_sub, i):
                result_list.append(('str_begin_without_sym_sub', i))
            elif re.fullmatch(spaceline, i):
                result_list.append(('spaceline', i))
            elif re.fullmatch(item_begin, i):
                result_list.append(('item_begin', i))
            else:
                result_list.append(('invaild', i))

    return ltmd2token(s)
