# distutils: language = c++
from libcpp.string cimport string

cdef extern from "inja_helpers.hpp":
    float test_cython()
    string test_render(string key) except +
    string test_render_wglobals(string temp_globals, string key) except +

def py_test_cython():
    return test_cython()

def py_test_render(key):
    return test_render(key.encode())

def py_test_render_wglobals(temp_globals, key):
    return test_render_wglobals(temp_globals.encode(), key.encode())

