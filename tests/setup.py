""""Setup script to cythonize the cpp to import as a module for testing"""
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize

EXT = Extension("tests.inja_test",
                sources=["./tests/inja_helpers.pyx"],
                include_dirs=["./tests/include/"],
                library_dirs=["./tests/include/"],
                language="c++",
                extra_compile_args=["-std=c++17"])

setup(name="inja_test",
      packages=find_packages(),
      ext_modules=cythonize(EXT, compiler_directives={"language_level": "3"}))
