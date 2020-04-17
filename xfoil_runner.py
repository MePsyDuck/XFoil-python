import os
import pty
import subprocess

from config import xfoil_path, parsed_files, step_size, smaller_step_size
from util import write2xfoil, parsed_file_path, seq, parsed_newpolar_file_path


def process_xfoil(xfoil, parsed_file, foil_name, alpha):
    write2xfoil(xfoil, 'LOAD ' + parsed_file_path(parsed_file))
    write2xfoil(xfoil, 'MDES')
    write2xfoil(xfoil, 'FILT')
    write2xfoil(xfoil, 'EXEC')
    write2xfoil(xfoil)
    write2xfoil(xfoil, 'PANE')
    write2xfoil(xfoil, 'OPER')
    write2xfoil(xfoil, 'ITER 500')
    write2xfoil(xfoil, 'RE 50000')
    write2xfoil(xfoil, 'VISC 50000')
    if alpha != 0:
        write2xfoil('ASEQ 0 ' + str(alpha - 0.25) + ' 0.25')
    write2xfoil(xfoil, 'PACC')
    write2xfoil(xfoil, parsed_newpolar_file_path(foil_name))
    write2xfoil(xfoil, '')
    write2xfoil(xfoil, 'ALFA ' + str(alpha))


def run_xfoil():
    with subprocess.Popen([xfoil_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=None, encoding='utf8') as xfoil:

        for i in range(1, len(parsed_files)):
            parsed_file = parsed_files[i]
            foil_name = parsed_file.split('.')[0]
            for alpha in seq(0, 20, step_size):
                process_xfoil(xfoil, parsed_file, foil_name, alpha)

                output = xfoil.stdout.readline(),

                if "VISCAL:  Convergence failed" in output:
                    for smaller_alpha in seq(alpha - 0.25, alpha, smaller_step_size):
                        process_xfoil(xfoil, parsed_file, foil_name, smaller_alpha)

            for alpha in seq(0, -20, -step_size):
                process_xfoil(xfoil, parsed_file, foil_name, alpha)

                output = xfoil.stdout.readline(),

                if "VISCAL:  Convergence failed" in output:
                    for smaller_alpha in seq(alpha + 0.25, alpha, -smaller_step_size):
                        process_xfoil(xfoil, parsed_file, foil_name, smaller_alpha)


if __name__ == '__main__':
    run_xfoil()
