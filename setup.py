"""Cython build file"""
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os

cythonExt = []
for root, dirs, files in os.walk(os.getcwd(), followlinks=True):
    for file in files:
        if file.endswith(".pyx") and ".pyenv" not in root:
            filePath = os.path.relpath(os.path.join(root, file))
            cythonExt.append(Extension(filePath.replace(("/", "\\")[os.name == 'nt'], ".")[:-4], [filePath]))

if __name__ == "__main__":
    setup(
        name="lets pyx modules",
        ext_modules=cythonize(cythonExt, nthreads=4, compiler_directives={"language_level": 3}),
    )
