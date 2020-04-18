import multiprocessing
import os
import signal
import time

import wexpect

from config import xfoil_path, step_size, smaller_step_size, XFOIL_C, MDES_C, POLAR_DUMP_P, POLAR_SAVE_P, ALFA_END, \
    batch_count, OPER_C
from util import parsed_file_path, seq, parsed_newpolar_file_path, get_unprocessed_files, chunk_it


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
        print('timeout for alpha : ' + str(alpha))
        return 1


def run_xfoil(parsed_files):
    xfoil = wexpect.spawn(xfoil_path, encoding='utf-8')
    with open('processed.txt', 'a') as processed:
        with open('unprocessed.txt', 'a') as unprocessed:
            for parsed_file in parsed_files:
                start = time.time()
                foil_name = parsed_file.split('.')[0]

                if load_file(xfoil, parsed_file, foil_name):
                    for alpha in seq(0, 20, step_size):
                        if change_alpha(xfoil, alpha) == 0:
                            for smaller_alpha in seq(alpha - 0.25, alpha, smaller_step_size):
                                change_alpha(xfoil, smaller_alpha)

                    for alpha in seq(0, -20, -step_size):
                        if change_alpha(xfoil, alpha) == 0:
                            for smaller_alpha in seq(alpha + 0.25, alpha, -smaller_step_size):
                                change_alpha(xfoil, smaller_alpha)
                else:
                    xfoil.kill(signal.SIGINT)
                    xfoil = wexpect.spawn(xfoil_path, encoding='utf-8')
                    end = time.time()
                    print(str(os.getpid()) + ': File was unprocessed ' + parsed_file + ' took ' + str(end - start))
                    unprocessed.write(parsed_file + '\n')
                    unprocessed.flush()
                    continue

                reset(xfoil)
                end = time.time()
                print(str(os.getpid()) + ': File ' + parsed_file + ' took ' + str(end - start))
                processed.write(parsed_file + '\n')
                processed.flush()


def make_processes():
    parsed_files = get_unprocessed_files()
    batches = chunk_it(parsed_files, batch_count)

    processes = []
    # creating processes
    for batch in batches:
        processes.append(multiprocessing.Process(target=run_xfoil, args=(batch,)))

    # starting process
    for process in processes:
        process.start()

    # wait until process is finished
    for process in processes:
        process.join()

    # all processes finished
    print("Done!")


if __name__ == '__main__':
    make_processes()
