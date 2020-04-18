import os

# Paths
import wexpect

cwd = os.getcwd()
lib_dir = os.path.join(cwd, 'lib')
xfoil_path = os.path.join(lib_dir, 'xfoil.exe')
parsed_dir = os.path.join(cwd, 'parsed')
new_polar_dir = 'newpolar'

# Limits
iterations = 1
step_size = 0.25
smaller_step_size = 0.1
batch_count = 5

# Constant prompts
XFOIL_C = ' XFOIL   c>'
MDES_C = '.MDES   c>'
OPERI_C = '.OPERi   c>'
OPERV_C = '.OPERv   c>'
OPERIA_C = '.OPERia   c>'
OPERVA_C = '.OPERva   c>'
OPER_C = [OPERIA_C, OPERVA_C, OPERV_C, OPERI_C]
POLAR_SAVE_P = 'Enter  polar save filename  OR  <return> for no file   s>'
POLAR_DUMP_P = 'Enter  polar dump filename  OR  <return> for no file   s>'
CONVERGENCE_FAILED_P = 'VISCAL:  Convergence failed'
ALFA_END = [CONVERGENCE_FAILED_P, OPERVA_C, OPERIA_C, wexpect.EOF]
