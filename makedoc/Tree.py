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