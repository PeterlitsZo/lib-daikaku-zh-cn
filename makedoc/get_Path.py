from pathlib import Path
from color import imp, sec

def get_parent_dir_ls(dir_str):
    dir_path = Path(dir_str)
    print('  :', imp(dir_path))

    result = list(dir_path.iterdir())
    result = sorted(result, key=lambda i: not('.ltmd' in i.name or '.txt' in i.name))
    result = sorted(result, key=lambda i: not i.is_dir())
    for index, i in enumerate(result):
        output_index = f'    [{index:3}]'
        output_name = i.name
        if i.is_dir():
            print(sec(output_index, '(dir)', output_name))
            continue

        if '.txt' in i.name or '.ltmd' in i.name:
            print(imp(output_index, output_name))
        else:
            print(output_index, output_name)
    return result

def get_file_path():
    dir_path = Path(__file__).parent
    print(imp("help: use '..' to reach the parent of this dir"))
    print(imp("help: or use the index to get the file or dir"))
    while True:
        dir_ls_list = get_parent_dir_ls(dir_path)
        input_ = input(imp('> '))
        try:
            if input_.isdigit():
                op_path = dir_ls_list[int(input_)]
                if op_path.is_file():
                    return op_path
                elif op_path.is_dir():
                    dir_path = op_path
                else:
                    raise KeyError
            elif input_ == '..':
                dir_path = dir_path.parent
            else:
                raise KeyError
        except KeyError:
            # error key
            print(imp('KeyError, Enter again'))