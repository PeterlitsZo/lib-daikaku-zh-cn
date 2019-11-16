import re
from collections import namedtuple


class Tree(object):
    def __init__(self, name = '', value = []):
        self.name = name
        self.value = value

    def is_left_node(self):
        return all([type(value_item) == str for value_item in self.value])

    def _Tree_graph_str(self):
        if self.is_left_node():
            value_list = ['\033[90m"\033[0m' + str_value + '\033[90m"\033[0m' for str_value in self.value]
            value_str = str.join("\033[90m, \033[0m", value_list)
            return f'- {self.name}: {value_str}'
        else:
            result = [f'- {self.name}:']
            for value_item in self.value:
                if type(value_item) == str:
                    result.append('    \033[90m"\033[0m' + value_item + '\033[90m"\033[0m')
                else:
                    result.append( '    ' + str.join('\n    ', value_item._Tree_graph_str().split('\n')) )
            return str.join('\n', result)
    
    def __str__(self):
        return f'<object Tree: {self.name}:[...]>:\n' + self._Tree_graph_str()

    def __repr__(self):
        if self.is_left_node():
            value_str = str.join(", ", self.value)
            return f'<{self.name}:[{value_str}]>'
        else:
            result = [f'<{self.name}:[ ']
            result_value = []
            for value_item in self.value:
                if type(value_item) == str:
                    result_value.append('"' + value_item + '"')
                else:
                    result_value.append(repr(value_item))
            result.append(str.join(', ', result_value))
            result.append(' ]>')
            return str.join('', result)


class scanner(object):
    def __init__(self, re_str_dict):
        self.re_str_dict = re_str_dict
    
    def get_result(self, string: str):
        result_list = []

        for line in string.split('\n'):
            for item in self.re_str_dict:
                if re.fullmatch(self.re_str_dict[item], line):
                    result_list.append(Tree(item, [line]))
                    break
                else:
                    continue
        return result_list


class parser(object):
    def __init__(self, tree_dict, reduce_tree_node_list):
        self.tree_dict = tree_dict
        self.reduce_tree_node_list = reduce_tree_node_list
        self._test = False

    def _get_full_tree(self, node:Tree, scanner_result: list, count = 0) -> (Tree, list):
        # Tree:name:[value]
        # if node is a left node -> if match then return left node's little tree
        if node.name not in self.tree_dict:
            if scanner_result[0].name != node.name:
                raise Exception('MatchError')
            else:
                if self._test:
                    print(" "*count*6 + ': \033[91m' + str(scanner_result[0].value) + '\033[0m')
                return scanner_result[0], scanner_result[1:]

        # if not then return a big tree
        else:
            # find a way to match the list
            for way in self.tree_dict[node.name]:
                # try the way
                node.value = [Tree(way_part) for way_part in way]
                if self._test:
                    print(f'{" "*count*6}\033[91m{count}: now in tree "{node.name}":\033[0m')
                    print(" "*count*6 + f'- {", ".join([i.name for i in node.value])}')
                # use the way to match it or fail
                scanner_result_back_up = scanner_result.copy()
                for i in range(len(node.value)):
                    try:
                        # if match one, the len of list(scanner_result) will -1
                        node.value[i], scanner_result = self._get_full_tree(node.value[i], scanner_result, count = count+1)
                    except Exception:
                        # failed to match it, then try another way
                        try_another_flag = True
                        scanner_result = scanner_result_back_up
                        break
                # no error, so break out
                else:
                    break
                if try_another_flag:
                    continue
            # there is no way to make it
            else:
                raise Exception('MatchError')
        return node, scanner_result

    def _run_with_tree(self, tree_node: Tree, func, *arg):
        # for each sub_node which is not str and is not the left:
        if type(tree_node.value) != str and any([type(i) != str for i in tree_node.value]):
            for sub_node_index, sub_node in enumerate(tree_node.value):
                if type(sub_node) == str:
                    continue
                else:
                    func(tree_node, sub_node_index, *arg)

    def _reduce_tree_node(self, tree_node, sub_tree_index, reduce_node_name:str) -> None:
        sub_tree = tree_node.value[sub_tree_index]
        if sub_tree.name == reduce_node_name:
            tree_node.value[sub_tree_index: sub_tree_index + 1] = sub_tree.value
        else:
            self._run_with_tree(sub_tree, self._reduce_tree_node, reduce_node_name)

    def _delete_tree_node(self, tree_node, sub_tree_index, delete_node_name:str) -> None:
        sub_tree = tree_node.value[sub_tree_index]
        if sub_tree.name == delete_node_name:
            del tree_node.value[sub_tree_index]
        else:
            self._run_with_tree(sub_tree, self._delete_tree_node, delete_node_name)

    def _change_tree_node(self, tree_node, sub_tree_index, changed_node_name:str, string:str) -> None:
        sub_tree = tree_node.value[sub_tree_index]
        if sub_tree.name == changed_node_name:
            sub_tree.name = string
        else:
            self._run_with_tree(sub_tree, self._change_tree_node, changed_node_name, string)

    def _get_reduced_tree(self, tree):
        for i in self.reduce_tree_node_list:
            if re.match(r'\(:delete item:\)', i):
                self._run_with_tree(tree, self._delete_tree_node, re.sub(r'\(:delete item:\)', '', i))
            if re.match(r'\(:change name to:([^:]*):\)', i):
                str_b, str_a = re.match(r'\(:change name to:([^:]*):\)(.*)', i).group(1, 2)
                self._run_with_tree(tree, self._change_tree_node, str_a, str_b)
            else:
                self._run_with_tree(tree, self._reduce_tree_node, i)
        return tree

    def get_tree(self, scanner_result: list):
        tree, _ = self._get_full_tree(Tree('Doc'), scanner_result)
        return self._get_reduced_tree(tree)


class ltmd_to_latex(object):
    def __init__(self, string:str):
        re_str_dict = {
            "line": r'-+\s*',
            "item_begin": r'-\s.*',
            "str_begin_with_sym_sub": r'-+[^-\s]+|-+[^-]+.+',
            "str_begin_without_sym_sub": r'[^-].*',
            "space_line": r'\s*'
        }
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
        reduce_tree_list = ['doc_parts', 'doc_part', 'strs', 'singlestr', 'str_begin_without_sym_sub',
                      'item_begin', 'item_begin', 'item_ends', 'items', 'item_end', 
                      'singlestr_no_items', 'strs_no_items',
                      '(:delete item:)space_lines', '(:delete item:)line', '(:delete item:)space_line',
                      '(:change name to:title:)title_no_items']
        self.scanner = scanner(re_str_dict)
        self.parser = parser(tree_dict, reduce_tree_list)
        self.string = string

    def _get_scanner_result(self):
        return self.scanner.get_result(self.string)

    def _get_parser_result(self):
        return self.parser.get_tree(self._get_scanner_result())

    def _get_string_of_Select_Part(self, tree):
        result_str = ''
        for item in tree.value:
            if item.name == 'title':
                result_str += ''.join(item.value) + '\n' + r'\hspace*{\fill}\mbox{(~~~~~~~~~~)}' + '\n'
                result_str += r'\begin{enumerate}[A.]' + '\n'
            else:
                item.value[0] = item.value[0][2:]
                result_str += '    \item ' + ''.join([i.lstrip() for i in item.value]) + '\n'
        result_str += r'\end{enumerate}'
        return result_str

    def _get_string_of_Fill_Part(self, tree):
        return ''.join(tree.value[0].value) + r'\_\_\_\_\_\_\_\_'

    def _get_string_of_Short_Question_Part(self, tree):
        return ''.join(tree.value[0].value)

    def _get_string_of_Question_Part(self, tree):
        result_str = ''
        for item in tree.value:
            if item.name == 'title':
                result_str += ''.join(item.value) + '\n'
                result_str += r'\begin{enumerate}[1)]' + '\n'
            else:
                item.value[0] = item.value[0][2:]
                result_str += '    \item ' + ''.join([i.lstrip() for i in item.value]) + '\n'
        result_str += r'\end{enumerate}'
        return result_str

    @staticmethod
    def _add_four_space(string:str):
        return '\n'.join(['    ' + i for i in string.split('\n')])
    
    def _get_latex(self):
        parser_tree = self._get_parser_result()

        result = ''
        for part in parser_tree.value:
            if part.name == 'Select Part':
                result += self._get_string_of_Select_Part(part)
            elif part.name == 'Fill Part':
                result += self._get_string_of_Fill_Part(part)
            elif part.name == 'Short Question Part':
                result += self._get_string_of_Short_Question_Part(part)
            elif part.name == 'Question Part':
                result += self._get_string_of_Question_Part(part)
            result += '\n' * 2

        result = "\\documentclass[a4paper]{ctexart}\n" \
                 "\n" \
                 "\n" \
                 "\\usepackage{amsmath}\n" \
                 "\\usepackage[shortlabels]{enumitem}\n" \
                 "\\usepackage{tikz}\n" \
                 "\\usepackage[normalem]{ulem}\n" \
                 "\\usepackage{xcolor}\n" \
                 "\\renewcommand{\\ULthickness}{2pt}\n" \
                 "\n" \
                 "\\setlist{leftmargin=4em, itemsep=0.1em, parsep=0em,\n" \
                 "    itemindent=0em, listparindent=0em,\n" \
                 "    labelwidth=1.5em, labelsep=1em}\n" \
                 "\n" \
                 "\\title{}\n" \
                 "\n" \
                 "\\begin{document}\n" + self._add_four_space(result) + '\\end{document}' 
        return result

    def out(self):
        return self._get_latex()

f = open(input('> '), 'r')
s = ltmd_to_latex(f.read()).out()
open(input('> '), 'w').write(s)
