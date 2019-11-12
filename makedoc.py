import re
from collections import namedtuple

# --- scanner ---
def ltmd_to_token(string:str) -> list:
    re_str = {
        "line": r'-+\s*',
        "item_begin": r'-\s.*',
        "str_begin_with_sym_sub": r'-+[^-\s]+|-+[^-]+.+',
        "str_begin_without_sym_sub": r'[^-].*',
        "space_line": r'\s*'
    }

    result_list = []
    Token = namedtuple('Token', ['token', 'value'])

    for line in string.split('\n'):
        for i in re_str:
            if re.fullmatch(re_str[i], line):
                result_list.append(Token(i, line))
                break
            else:
                continue
    return result_list


# --- parser ---
def token_to_tree(token_list:list) -> tuple:
    tree_dict = {
        'Doc': [['doc_parts']],
        'doc_parts': [['space_lines', 'doc_part', 'doc_parts'],
                      ['space_lines', 'doc_part', 'space_lines']],
        'doc_part': [['Select Part'],
                     ['Fill Part'],
                     ['Question Part'],
                     ['Short Question Part']],

        'space_lines': [['space_line', 'space_lines'],
                        ['space_line'],
                        []],

        'Select Part': [['title', 'line', 'items']],
        'Fill Part': [['title', 'line']],
        'Question Part': [['title_no_items', 'items']],
        'Short Question Part': [['title']],

        'title': [['strs']],
        'title_no_items': [['strs_no_items']],

        'items': [['item', 'items'],
                  ['item']],
        'item': [['item_begin', 'item_ends'],
                 ['item_begin']],
        'item_ends': [['str_begin_without_sym_sub', 'item_ends'],
                      ['str_begin_with_sym_sub', 'item_ends'],
                      ['str_begin_without_sym_sub'],
                      ['str_begin_with_sym_sub']],

        'strs': [['singlestr', 'strs'],
                 ['singlestr']],
        'strs_no_items': [['singlestr_no_items', 'strs_no_items'],
                          ['singlestr_no_items']],
        'singlestr': [['str_begin_without_sym_sub'],
                      ['item_begin'],
                      ['str_begin_with_sym_sub']],
        'singlestr_no_items': [['str_begin_without_sym_sub'],
                               ['str_begin_with_sym_sub']]
    }

    Tree = namedtuple('Tree', ['name', 'value'])
    result_tree = Tree('Doc', [])

    def get_tree(node:Tree, current_list: list, count:int) -> tuple:
        count = count + 1
        # if node is a left node -> if match then return left node's little tree
        if node.name not in tree_dict:
            if current_list[0].token != node.name:
                raise Exception('MatchError')
            else:
                node.value.clear()
                node.value.append(current_list[0].value)
                # ------------------------------------------------------------------------------
                # print(" "*count*6 + ': \033[91m' + current_list[0].value + '\033[0m')
                # ------------------------------------------------------------------------------
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
                # print(f'{" "*count*6}\033[0;31;40m{count}:current tree:(in {node.name}):\033[0m')
                # print(" "*count*6 + f'- {", ".join([i.name for i in node.value])}')
                # ------------------------------------------------------------------------------
                # use the way to match it or fail
                current_list_back_up = current_list.copy()
                for i in range(len(node.value)):
                    try:
                        # if match one, the len of list(current_list) will -1
                        node.value[i], current_list = get_tree(node.value[i], current_list, count)
                    except Exception:
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
    return tree


# --- parser ---
def tree_to_latex_tree(tree_list: tuple) -> tuple:
    # latex_tree:
    # doc:
    #     - (...) part:
    #         - title:
    #             - strs
    #         (there is not 'line' element)
    #         - items:(if the part is ...)
    #             - item
    #             - item
    #     - ...

    # Tree = namedtuple('Tree', ['name', 'value'])
    # --- reduce the spaceline ---
    def reduce_node(tree_node: tuple, node_name: str) -> None:
        if type(tree_node.value[0]) != str:
            for sub_node_index, sub_node in enumerate(tree_node.value):
                if sub_node.name == node_name:
                    del tree_node.value[sub_node_index]
                else:
                    reduce_node(sub_node, node_name)

    def change_tree(tree_node: tuple, node_name: str, to_change_str: str) -> None:
        Tree = namedtuple('Tree', ['name', 'value'])
        if type(tree_node.value[0]) != str:
            for sub_node_index, sub_node in enumerate(tree_node.value):
                if sub_node.name == node_name:
                    tree_node.value[sub_node_index] = Tree(to_change_str, sub_node.value)
                else:
                    change_tree(sub_node, node_name, to_change_str)

    def down_tree(tree_node: tuple, tree_name: str, do_not_down_the_first = False) -> None:
        # temp = [type(i) != str for i in tree_node.value]
        if type(tree_node.value) != str and True in [type(i) != str for i in tree_node.value]:
            for sub_node_index, sub_node in enumerate(tree_node.value):
                if type(sub_node) == str:
                    continue
                if sub_node.name == tree_name:
                    if not do_not_down_the_first:
                        tree_node.value[sub_node_index: sub_node_index + 1] = sub_node.value
                    else:
                        do_not_down_the_first = False
                        down_tree(sub_node, tree_name)
                else:
                    dndtf = do_not_down_the_first
                    down_tree(sub_node, tree_name, do_not_down_the_first = dndtf)

    reduce_node(tree_list, 'space_lines')
    reduce_node(tree_list, 'line')

    down_tree_list = ['doc_parts', 'doc_part', 'strs', 'singlestr', 'str_begin_without_sym_sub',
                      'item_begin', 'item_begin', 'item_end', 'items', 'item_ends', 
                      'singlestr_no_items', 'strs_no_items']
    for i in down_tree_list:
        down_tree(tree_list, i)
        
    change_tree(tree_list, 'title_no_items', 'title')

    return tree_list

# --- latexer ---
def latex_tree_to_latex(tree_list: tuple) -> str:
    result_str = '\n'
    if tree_list.name == 'Doc':
        result_str += r'\begin{enumerate}[1.]' + '\n'
        for i in tree_list.value:
            if i.name == 'Select Part':
                for j in i.value:
                    if j.name == 'title':
                        result_str += ''.join(j.value) + r'\hspace*{\fill}\mbox{(~~~~~~~~~~)}' + '\n'
                        result_str += r'\begin{enumerate}[A.]' + '\n'
                    if j.name == 'item':
                        result_str += '\item' + ''.join(j.value) + '\n'
                result_str += r'\end{enumerate}' + '\n'
            if i.name == 'Fill Part':
                for j in i.value:
                    result_str += ''.join(j.value) + r'\_\_\_\_\_\_\_\_' + '\n'
            if i.name == 'Short Question Part':
                for j in i.value:
                    result_str += ''.join(j.value) + '\n'
            if i.name == 'Question Part':
                for j in i.value:
                    if j.name == 'title':
                        result_str += ''.join(j.value) + '\n'
                        result_str += r'\begin{enumerate}[A.]' + '\n'
                    if j.name == 'item':
                        result_str += '\item' + ''.join(j.value) + '\n'
                result_str += r'\end{enumerate}' + '\n'
        result_str += r'\begin{enumerate}' + '\n'
    else:
        raise Exception('the first label should be "Doc"')
    return result_str


# --- mainer ---
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
    |   \begin{enumerate}
    |       $1+1=$
    |       \hspace*{\fill}\mbox{(~~~~~~~~~~)}
    |       \begin{enumerate}[A.]
    |           \item $2$
    |           \item $\lim_{x\to 0} f(x)=x$
    |           \item maybe 4
    |           \item there is no corrent anwser
    |       \end{enumerate}
    |   \end{enumerate}
    """
    ltmd_token = ltmd_to_token(ltmd_string)
    ltmd_tree = token_to_tree(ltmd_token)
    ltmd_latex_tree = tree_to_latex_tree(ltmd_tree)
    ltmd_latex = latex_tree_to_latex(ltmd_latex_tree)
    return ltmd_latex


def read_tree(tree, counter = 0) -> None:
    if type(tree) == str:
        print(' ' * 4 * counter, tree)
    elif all([type(i) == str for i in tree.value]):
        print(' ' * 4 * counter, tree.name, ': ', end='')
        print(str.join(' \033[90m(:newline:)\033[0m ', [i for i in tree.value]))
    else:
        print(' ' * 4 * counter, tree.name)
        for i in tree.value:
            read_tree(i, counter = counter + 1)


string = \
r"""
$1+1=$
-------------------------
- $2$
- $\lim_{x\to 0} f(x)=x$
- maybe 4
- there is no corrent anwser
  (... think more!)

$1+1=$
-------------------------

how to think about '1+1=2'?

tell me ...
- 1+2=?
- 2+2=?
"""
if __name__ == '__main__':
    i = ltmd_to_latex(string)
    read_tree(i)