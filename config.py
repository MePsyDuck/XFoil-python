import os

# Paths
import wexpect

cwd = os.getcwd()
lib_dir = os.path.join(cwd, 'lib')
xfoil_path = os.path.join(lib_dir, 'xfoil.exe')
parsed_dir = os.path.join(cwd, 'parsed')
new_polar_dir = 'newpolar'

# Limits
start = 0
end = 20
step_size = 0.25
smaller_step_size = 0.1
max_restarts = 5

# Constant prompts
XFOIL_C = ' XFOIL   c>'
MDES_C = '.MDES   c>'
OPER_C = r'\.OPER[iva]*   c>'
POLAR_SAVE_P = 'Enter  polar save filename  OR  <return> for no file   s>'
POLAR_DUMP_P = 'Enter  polar dump filename  OR  <return> for no file   s>'
CONVERGENCE_FAILED_P = r'VISCAL:  Convergence failed[\s]+[\r\n]+' + OPER_C
ALFA_P = [OPER_C, CONVERGENCE_FAILED_P, wexpect.EOF, wexpect.TIMEOUT]
