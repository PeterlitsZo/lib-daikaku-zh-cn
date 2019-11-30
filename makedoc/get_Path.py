from pathlib import Path

def get_parent_dir_ls(file_str):
    dir_path = Path(file_str).parent
    result = list(dir_path.iterdir())
    for index, i in enumerate(result):
        if '.txt' in i.name or '.ltmd' in i.name:
            print(f' * [{index:3}] {i.name}')
        else:
            print(f'   [{index:3}] {i.name}')
    return result