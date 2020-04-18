import multiprocessing
import time

import wexpect

from config import xfoil_path, step_size, smaller_step_size, XFOIL_C, MDES_C, POLAR_DUMP_P, POLAR_SAVE_P, ALFA_END, \
    OPER_C
from util import parsed_file_path, seq, parsed_newpolar_file_path, get_unprocessed_files


def load_file(xfoil, parsed_file, foil_name):
    xfoil.expect(XFOIL_C)
    xfoil.sendline('LOAD ' + parsed_file_path(parsed_file))
    xfoil.expect(XFOIL_C)
    xfoil.sendline('MDES')
    if xfoil.expect([MDES_C, wexpect.EOF, wexpect.TIMEOUT], timeout=120) != 0:
        return False
    xfoil.sendline('FILT')
    xfoil.expect(MDES_C)
    xfoil.sendline('EXEC')
    xfoil.expect(MDES_C)
    xfoil.sendline('')
    xfoil.expect(XFOIL_C)
    xfoil.sendline('PANE')
    xfoil.expect(XFOIL_C)
    xfoil.sendline('OPER')
    xfoil.expect(OPER_C)
    xfoil.sendline('ITER 500')
    xfoil.expect(OPER_C)
    xfoil.sendline('RE 50000')
    xfoil.expect(OPER_C)
    xfoil.sendline('VISC 50000')
    xfoil.expect(OPER_C)
    xfoil.sendline('PACC')
    xfoil.expect(POLAR_SAVE_P)
    xfoil.sendline(parsed_newpolar_file_path(foil_name))
    xfoil.expect(POLAR_DUMP_P)
    xfoil.sendline('')
    xfoil.expect(OPER_C)
    return True


def reset(xfoil):
    xfoil.sendline('')


def change_alpha(xfoil, alpha):
    xfoil.sendline('ALFA ' + str(alpha))
    try:
        return xfoil.expect(ALFA_END, timeout=120)
    except wexpect.wexpect_util.TIMEOUT:
        return -1


def run_sequence(xfoil, p_index, foil_name, start, end, step_size_, smaller_step_size_):
    for alpha in seq(start, end, step_size_):
        if change_alpha(xfoil, alpha) == 0:
            for smaller_alpha in seq(alpha - step_size_, alpha, smaller_step_size_):
                if change_alpha(xfoil, smaller_alpha) == -1:
                    print(str(p_index) + ': File timed out: ' + foil_name + ' smaller_alpha: ' + str(smaller_alpha))
        else:
            print(str(p_index) + ': File timed out: ' + foil_name + ' alpha: ' + str(alpha))


def run_xfoil(p_index, parsed_file):
    start = time.time()
    xfoil = wexpect.spawn(xfoil_path, encoding='utf-8')
    foil_name = parsed_file.split('.')[0]

    if load_file(xfoil, parsed_file, foil_name):

        run_sequence(xfoil, p_index, foil_name, 0, 20, step_size, smaller_step_size)
        run_sequence(xfoil, p_index, foil_name, 0, -20, -step_size, -smaller_step_size)

        end = time.time()
        print(str(p_index) + ': ' + foil_name + ' processed. Took: ' + str(end - start) + ' seconds')
        with open('processed.txt', 'a') as processed:
            processed.write(parsed_file + '\n')
        return str(p_index) + ': ' + foil_name + ' processed.'

    else:
        print(str(p_index) + ': ' + foil_name + ' processing failed.')
        with open('unprocessed.txt', 'a') as unprocessed:
            unprocessed.write(parsed_file + '\n')
        return str(p_index) + ': ' + foil_name + ' failed.'


if __name__ == '__main__':
    parsed_files = get_unprocessed_files()

    print('Processing ' + str(len(parsed_files)) + ' files')

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.starmap(run_xfoil, enumerate(parsed_files))

    print('Done!')
