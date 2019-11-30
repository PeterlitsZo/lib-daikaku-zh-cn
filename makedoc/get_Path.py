from pathlib import Path
from color import imp

def get_parent_dir_ls(file_str):
    dir_path = Path(file_str).parent
    result = list(dir_path.iterdir())
    for index, i in enumerate(result):
        output = f'   [{index:3}] {i.name}'
        if '.txt' in i.name or '.ltmd' in i.name:
            print(imp(output))
        else:
            print(output)
    return result