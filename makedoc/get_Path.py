from pathlib import Path

def get_parent_dir_ls(file_str):
    dir_path = Path(file_str).parent
    result = list(dir_path.iterdir())
    for index, i in enumerate(result):
        if '.txt' in i.name or '.ltmd' in i.name:
            print(f'\033[91m[{index:3}] {i.name}\033[0m')
        else:
            print(f'[{index:3}] {i.name}')
    return result