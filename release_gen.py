import os
import shutil
from distutils.dir_util import copy_tree
import setup
from rustplus.module_info import ModuleInfo


version = ModuleInfo.__version__

# Wipe and create new link to src dir
shutil.rmtree("src", ignore_errors=True)
version_string = f"V{version.replace('.', '_').replace('-', '_')}"
new_dir = f"src{os.sep}rustplus{os.sep}{version_string}"

for path in ["src", "src/rustplus"]:
    os.mkdir(f"{os.path.dirname(os.path.realpath(__file__))}/{path}")

# Loop through all the files
for file in os.listdir(f"rustplus"):
    file_path = f"rustplus{os.sep}{file}"
    # If it is a file, it's most likely the __init__.py, therefore just copy it
    if os.path.isfile(file_path):
        if file == "module_info.py":
            shutil.copy(file_path, f"{new_dir}{os.sep}{file}", follow_symlinks=True)
        else:
            shutil.copy(file_path, f"src{os.sep}rustplus", follow_symlinks=True)
    else:
        # This means it's a directory, so copy it as a tree
        copy_tree(file_path, f"{new_dir}{os.sep}{file}")

with open(f"{new_dir}{os.sep}__init__.py", "w") as new_package:
    new_package.writelines(["from . import *\n"])

with open(f"src{os.sep}rustplus{os.sep}__init__.py", "r") as input_file:
    data = []
    for line in input_file.readlines():
        if line.startswith("from"):
            index = line.find(".")
            data.append(f"{line[:index + 1]}{version_string}.{line[index + 1:]}")
        elif "__name__" in line:
            data.append(f"__name__ = '{ModuleInfo.__module_name__}'\n")
        elif "__version__" in line:
            data.append(f"__version__ = '{ModuleInfo.__version__}'\n")
        elif "__author__" in line:
            data.append(f"__author__ = '{ModuleInfo.__author__}'\n")
        elif "__support__" in line:
            data.append(f"__support__ = '{ModuleInfo.__support__}'\n")
        else:
            data.append(line)

with open(f"src{os.sep}rustplus{os.sep}__init__.py", "w") as output_file:
    output_file.writelines(data)

with open(f"{new_dir}{os.sep}module_info.py", "r") as input_file:
    data = []
    for line in input_file.readlines():
        if "__dev__" in line:
            data.append("    __dev__ = False\n")
        else:
            data.append(line)

with open(f"{new_dir}{os.sep}module_info.py", "w") as output_file:
    output_file.writelines(data)

setup.main()
