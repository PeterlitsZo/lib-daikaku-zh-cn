import re
from Tree import Tree

class Scanner(object):
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