import re
from collections import namedtuple

# --- scanner ---
def ltmd_to_token(string:str) -> list:
    re_str = {
        "line": r'-+\s*',
        "item_begin": r'-\s.*',
        "str_begin_with_sym_sub": r'-+[^-\s]+|-+[^-]+.+',
        "str_begin_without_sym_sub": r'[^-].*',
        "spaceline": r'\s*'
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
        'Select Part': [['title', 'line', 'items']],
        'Fill Part': [['title', 'line']],
        'Question Part': [['title', 'items']],
        'Short Question Part': [['title']],
        'part':[['Select Part'],
                ['Fill Part'],
                ['Question Part'],
                ['Short Question Part']],
        'spacelines': [['spaceline', 'spacelines'],
                       ['spaceline']],
        'singletree': [['spacelines', 'part', 'spacelines'],
                       ['spacelines', 'part'],
                       ['part', 'spacelines'],
                       ['part']],
        'trees': [['singletree', 'trees'],
                  ['singletree']],
        'doc': [['trees']]
    }

    Tree = namedtuple('Tree', ['name', 'value'])
    result_tree = Tree('doc', [])

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
                # print(f'{" "*count*6}{count}:current tree:(in {node.name}):')
                # for i in node.value:
                #     print(" "*count*6 + '-', end = '')
                #     print(i)
                # ------------------------------------------------------------------------------
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
    return tree


# --- parser ---
def tree_to_latex_tree(tree_list: tuple) -> tuple:
    # latex_tree:
    # doc:
    #     - part:
    #         - (...) title:
    #             - strs
    #         (there is not 'line' element)
    #         - items:(if the title is ...)
    #             - item
    #             - item

    # Tree = namedtuple('Tree', ['name', 'value'])
    # --- reduce the spaceline ---
    def reduce_node(tree_node: tuple, node_name: str) -> None:
        if type(tree_node.value[0]) != str:
            for sub_node_index, sub_node in enumerate(tree_node.value):
                if sub_node.name == node_name:
                    del tree_node.value[sub_node_index]
                else:
                    reduce_node(sub_node, node_name)

    def down_tree(tree_node: tuple, tree_name: str, do_not_down_the_first = False) -> None:
        if type(tree_node.value[0]) != str:
        # if all([type(i) == str for i in tree_node.value]) == True:
            for sub_node_index, sub_node in enumerate(tree_node.value):
                if sub_node.name == tree_name:
                    if not do_not_down_the_first:
                        tree_node.value[sub_node_index: sub_node_index + 1] = sub_node.value
                    else:
                        do_not_down_the_first = False
                        down_tree(sub_node, tree_name)
                else:
                    dndtf = do_not_down_the_first
                    down_tree(sub_node, tree_name, do_not_down_the_first = dndtf)

    reduce_node(tree_list, 'spacelines')
    reduce_node(tree_list, 'line')
    down_tree(tree_list, 'trees')
    down_tree(tree_list, 'strs')
    down_tree(tree_list, 'singlestr')
    down_tree(tree_list, 'str_begin_without_sym_sub')
    down_tree(tree_list, 'item_begin')
    down_tree(tree_list, 'singletree')
    down_tree(tree_list, 'items', do_not_down_the_first = True)
    down_tree(tree_list, 'item')
    down_tree(tree_list, 'part')
    return tree_list

# --- latexer ---
def latex_tree_to_latex(tree_list: tuple) -> str:
    pass


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
    ltmd_latex_tree = tree_to_latex_tree(ltmd_tree)
    ltmd_latex = latex_tree_to_latex(ltmd_latex_tree)
    return ltmd_latex

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
    print(tree_to_latex_tree(token_to_tree(ltmd_to_token(string))))