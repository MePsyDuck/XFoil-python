import os

import subprocess

# Paths
cwd = os.getcwd()
lib_dir = os.path.join(cwd, 'lib')
xfoil_path = os.path.join(lib_dir, 'xfoil.exe')
output_dir = os.path.join(cwd, 'output')
parsed_dir = os.path.join(cwd, 'parsed')
parsed_files = os.listdir(parsed_dir)
new_polar_dir = os.path.join(cwd, 'newpolar')

# Limits
iterations = 1
step_size = 0.25
smaller_step_size = 0.1

