from collections import namedtuple
from Scanner import Scanner
from Parser import Parser
from get_Path import get_parent_dir_ls
import subprocess


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
        self.scanner = Scanner(re_str_dict)
        self.parser = Parser(tree_dict, reduce_tree_list)
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
        return self._add_four_space(result_str)

    def _get_string_of_Fill_Part(self, tree):
        return self._add_four_space(''.join(tree.value[0].value) + r'\_\_\_\_\_\_\_\_')

    def _get_string_of_Short_Question_Part(self, tree):
        return self._add_four_space(''.join(tree.value[0].value))

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
        return self._add_four_space(result_str)

    @staticmethod
    def _add_four_space(string:str):
        return '\n'.join(['    ' + i for i in string.split('\n')])
    
    def _get_latex(self):
        parser_tree = self._get_parser_result()

        result = ''
        for part in parser_tree.value:
            result += '\\item\n'
            if part.name == 'Select Part':
                result += self._get_string_of_Select_Part(part)
            elif part.name == 'Fill Part':
                result += self._get_string_of_Fill_Part(part)
            elif part.name == 'Short Question Part':
                result += self._get_string_of_Short_Question_Part(part)
            elif part.name == 'Question Part':
                result += self._get_string_of_Question_Part(part)
            result += '\n' * 2
        result = '\\begin{enumerate}[1., leftmargin = 4em]\n' + self._add_four_space(result) + '\\end{enumerate}\n'

        result = "\\documentclass[a4paper]{ctexart}\n" \
                 "\n" \
                 "\n" \
                 "\\usepackage{amsmath}\n" \
                 "\\usepackage[shortlabels]{enumitem}\n" \
                 "\\usepackage{tikz}\n" \
                 "\\usepackage[normalem]{ulem}\n" \
                 "\n" \
                 "\\setlist{leftmargin=2em, itemsep=0.1em, parsep=0em,\n" \
                 "    itemindent=0em, listparindent=0em,\n" \
                 "    labelwidth=1.5em, labelsep=1em}\n" \
                 "\n" \
                 "\\newcommand{\\ul}{\\uline{~~~~~~~~~~~~~~~~}}\n" \
                 "\n" \
                 "\n" \
                 "\\title{}\n" \
                 "\n" \
                 "\\begin{document}\n" + self._add_four_space(result) + '\n\\end{document}' 
        return result

    def out(self):
        return self._get_latex()

if __name__ == '__main__':
    parent_dir_list = get_parent_dir_ls(__file__)
    op_file = parent_dir_list[int(input('> '))]
    f = open(op_file, 'r', encoding='UTF-8')

    s = f.read()
    s = ltmd_to_latex(s).out()

    open(op_file.with_suffix('.tex'), 'w', encoding='UTF-8').write(s)

    print(op_file)
    subprocess.run(f"xelatex {op_file.with_suffix('.tex')}", cwd = op_file.parent)
    subprocess.run(f"xelatex {op_file.with_suffix('.tex')}", cwd = op_file.parent)

    suffix = ['.aux', '.log', 'fdb_latexmk', 'fls', 'tex']
    for i in suffix:
        try:
            op_file.with_suffix(i).unlink()
        except:
            pass
