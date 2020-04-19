import multiprocessing
import signal
import time

import wexpect

from config import xfoil_path, step_size, smaller_step_size, XFOIL_C, MDES_C, POLAR_DUMP_P, POLAR_SAVE_P, ALFA_P, \
    OPER_C, max_restarts, start, end
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


def init(xfoil):
    xfoil.sendline('INIT')


def change_alpha(xfoil, alpha):
    xfoil.sendline('ALFA ' + str(alpha))
    try:
        return xfoil.expect(ALFA_P, timeout=120)
    except wexpect.wexpect_util.TIMEOUT:
        return -1


def restart_xfoil(xfoil, p_index, foil_name, parsed_file, restarts):
    if restarts < max_restarts:
        xfoil.kill(signal.SIGINT)
        xfoil = wexpect.spawn(xfoil_path, encoding='utf-8')
        load_file(xfoil, parsed_file, foil_name)
        init(xfoil)
        return xfoil
    else:
        raise Exception('{0:4d}: File: {1:20s} was restarted too many times.'.format(p_index, foil_name))


def run_sequence(xfoil, p_index, foil_name, parsed_file, start_, end_, step_size_, smaller_step_size_):
    restarts = 0

    for alpha in seq(start_, end_, step_size_):
        result = change_alpha(xfoil, alpha)
        if result == 0:
            continue
        elif result == 1:
            print('{0:4d}: File: {1:20s} convergence failed for alpha: {2:5f}'.format(p_index, foil_name, alpha))
            for smaller_alpha in seq(alpha - step_size_, alpha, smaller_step_size_):
                result_inner = change_alpha(xfoil, smaller_alpha)
                if result_inner == 1:
                    print('{0:4d}: File: {1:20s} convergence failed for smaller_alpha: {2:5f}'.format(p_index,
                                                                                                      foil_name,
                                                                                                      smaller_alpha))
                elif result_inner != 0:
                    xfoil = restart_xfoil(xfoil, p_index, foil_name, parsed_file, restarts)
                    restarts += 1
                    print('{0:4d}: File: {1:20s} timed out/EOF for smaller_alpha: {2:5f}'.format(p_index,
                                                                                                 foil_name,
                                                                                                 smaller_alpha))
        else:
            xfoil = restart_xfoil(xfoil, p_index, foil_name, parsed_file, restarts)
            restarts += 1
            print('{0:4d}: File: {1:20s} timed out/EOF for alpha: {2:5f}'.format(p_index, foil_name, alpha))
    return xfoil


def run_xfoil(p_index, parsed_file):
    xfoil = wexpect.spawn(xfoil_path, encoding='utf-8')

    start_time = time.time()
    foil_name = parsed_file.split('.')[0]

    if load_file(xfoil, parsed_file, foil_name):
        try:
            xfoil = run_sequence(xfoil, p_index, foil_name, parsed_file, start, end, step_size, smaller_step_size)
            run_sequence(xfoil, p_index, foil_name, parsed_file, start, -end, -step_size, -smaller_step_size)
        except Exception as ex:
            print(str(ex))
            with open('unprocessed.txt', 'a') as unprocessed:
                unprocessed.write(parsed_file + '\n')
            return str(ex)

        end_time = time.time()
        print('{0:4d}: File: {1:20s} processed. Took: {2:5f} seconds'.format(p_index, foil_name, end_time - start_time))
        with open('processed.txt', 'a') as processed:
            processed.write(parsed_file + '\n')
        return '{0:4d}: {1:20s} processed.'.format(p_index, foil_name)

    else:
        print('{0:4d}: File: {1:20s} processing failed.'.format(p_index, foil_name))
        with open('unprocessed.txt', 'a') as unprocessed:
            unprocessed.write(parsed_file + '\n')
        return '{0:4d}: {1:20s} failed.'.format(p_index, foil_name)


if __name__ == '__main__':
    parsed_files = get_unprocessed_files()

    print('Processing {0} files'.format(len(parsed_files)))

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.starmap(run_xfoil, enumerate(parsed_files))

    with open('output.txt', 'a') as output:
        output.writelines(pool)

    print('Done!')
