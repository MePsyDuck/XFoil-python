import os

from config import output_dir, parsed_dir, new_polar_dir


def write2xfoil(xfoil, cmd=''):
    xfoil.stdin.write('{0}\n'.format(cmd))


def output_file_path(file_name):
    return os.path.join(output_dir, file_name)


def parsed_file_path(file_name):
    return os.path.join(parsed_dir, file_name)


def parsed_newpolar_file_path(file_name):
    return os.path.join(new_polar_dir, file_name, file_name + '_50000.dat')


def seq(start, stop, step=1):
    n = int(round((stop - start) / float(step)))
    if n > 1:
        return [start + step * i for i in range(n + 1)]
    elif n == 1:
        return [start]
    else:
        return []
