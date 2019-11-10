import re
from collections import namedtuple

def ltmd_to_token(string:str) -> list:
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

    result_list = []
    Token = namedtuple('Token', ['token', 'value'])

    for i in string.split('\n'):
        if re.fullmatch(line, i):
            result_list.append(Token('line', i))
        elif re.fullmatch(item_begin, i):
            result_list.append(Token('item_begin', i))
        elif re.fullmatch(str_begin_with_sym_sub, i):
            result_list.append(Token('str_begin_with_sym_sub', i))
        elif re.fullmatch(str_begin_without_sym_sub, i):
            result_list.append(Token('str_begin_without_sym_sub', i))
        elif re.fullmatch(spaceline, i):
            result_list.append(Token('spaceline', i))
        else:
            result_list.append(Token('invaild', i))
    return result_list


def token_to_tree(token_list:list) -> tuple:
    Tree = namedtuple('Tree', ['name', 'value'])
    tree_dict = {
        'singlestr': [['str_begin_without_sym_sub'],
                      ['item_begin'],
                      ['str_begin_with_sym_sub']],
        'strs': [['singlestr', 'strs'],
                 ['singlestr']],
        'title': [['strs']],
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
        'singletree': [['spacelines', 'valid', 'spacelines'],
                       ['spacelines', 'valid'],
                       ['valid', 'spacelines'],
                       ['valid']],
        'trees': [['singletree', 'trees'],
                  ['singletree']]
    }

    result_tree = Tree('trees', [])

    def get_tree(node:Tree, current_list: list, count:int) -> tuple:
        count = count + 1
        # if node is a left node -> if match then return left node's little tree
        if node.name not in tree_dict:
            if current_list[0].token != node.name:
                raise Exception('MatchError')
            else:
                node.value.append(current_list[0].value)
                return node, current_list[1:]

        # if not then return a big tree
        else:
            # find a way to match the list
            for i in tree_dict[node.name]:
                # try the way
                node.value.clear()
                for i_str in i:
                    node.value.append(Tree(i_str, []))
                # ------------------------------------------------------------------------------
                # print(f'{" "*count*6}{count}:current tree:(in {node.name})------------------------------------')
                # for i in node.value:
                #     print(" "*count*6 + '-', end = '')
                #     print(i)
                # ------------------------------------------------------------------------------
                print('.', end='')
                # use the way to match it or fail
                current_list_back_up = current_list.copy()
                for i in range(len(node.value)):
                    try:
                        # if match one, the len of list will -1
                        node.value[i], current_list = get_tree(node.value[i], current_list, count)
                    except Exception as ex:
                        # failed to match it, then try another way
                        try_another_flag = True
                        current_list = current_list_back_up
                        break
                # no error, so break out
                else:
                    break
                if try_another_flag:
                    continue
            # there is no way to make it
            else:
                raise Exception('MatchError')
        return node, current_list
    
    tree, _ = get_tree(result_tree, token_list, 0)
    print()
    return tree


def tree_to_latex(tree_list: list) -> str:
    pass


def ltmd_to_latex(ltmd_string:str) -> str:
    r"""
    input will like:(or something else)
    |   version = v0.0.1
    |   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    ltmd_token = ltmd_to_token(ltmd_string)
    ltmd_tree = token_to_tree(ltmd_token)
    ltmd_latex = tree_to_latex(ltmd_tree)
    return ltmd_latex

if __name__ == '__main__':
    string = \
    "balabala" \
    "- how about this?\n" \
    "--------------------------\n" \
    "- a\n" \
    "- b\n" \
    "- c\n" \
    "- d\n"
    print('-------------------------------------------')
    def print_tree(tree, count):
        if type(tree[1][0]) == str:
            print(' ' * 4 * count, tree[0], tree[1][0])
        else:
            print(' ' * 4 * count, tree[0], '--------------------------')
            for i in tree[1]:
                print_tree(i, count + 1)
    print(token_to_tree(ltmd_to_token(string)))
    print_tree(token_to_tree(ltmd_to_token(string)), count=1)