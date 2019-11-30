import re
from Tree import Tree
from color import imp


class Parser(object):
    def __init__(self, tree_dict, reduce_tree_node_list):
        self.tree_dict = tree_dict
        self.reduce_tree_node_list = reduce_tree_node_list
        self._test = True

    def _get_full_tree(self, node:Tree, scanner_result: list, count = 0) -> (Tree, list):
        # Tree:name:[value]
        # if node is a left node -> if match then return left node's little tree
        if node.name not in self.tree_dict:
            if scanner_result[0].name != node.name:
                raise Exception('MatchError')
            else:
                if self._test:
                    print(" "*count*4 + ': ' + imp(str(scanner_result[0].value)))
                return scanner_result[0], scanner_result[1:]

        # if not then return a big tree
        else:
            # find a way to match the list
            for way in self.tree_dict[node.name]:
                # try the way
                node.value = [Tree(way_part) for way_part in way]
                if self._test:
                    print(" "*count*4 + imp(str(count) + ":now in tree" + node.name))
                    print(" "*count*4 + f'- {", ".join([i.name for i in node.value])}')
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