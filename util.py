import os
import shutil

from config import parsed_dir, new_polar_dir


def parsed_file_path(file_name):
    return os.path.join(parsed_dir, file_name)


def parsed_newpolar_file_path(file_name):
    dir_path = os.path.join(new_polar_dir, file_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    file_path = os.path.join(dir_path, file_name + '_50000.dat')
    return file_path


def get_unprocessed_files():
    with open('processed.txt', 'r') as processed:
        parsed_files = os.listdir(parsed_dir)
        processed_files = processed.read().splitlines()
        files = [file for file in parsed_files if file not in processed_files]

    with open('unprocessed.txt', 'r') as unprocessed:
        unprocessed_files = unprocessed.read().splitlines()
        files = [file for file in files if file not in unprocessed_files]

    remove_partial_processed_files(files)
    return files


def remove_partial_processed_files(parsed_files):
    for file in parsed_files:
        shutil.rmtree(file)


def seq(start, stop, step=1):
    n = int(round((stop - start) / float(step)))
    if n > 1:
        return [start + step * i for i in range(n + 1)]
    elif n == 1:
        return [start]
    else:
        return []
