
cdef extern from "Python.h":
    ctypedef int Py_ssize_t

cimport buffers

def checkbuffer3(object o):
    return buffers.PyObject_CheckBuffer(o)

def checkbuffer2(object o):
    return buffers.PyObject_CheckReadBuffer(o)

def is_buffer(object obj):
    return buffers.is_buffer(obj)

def asbuffer_r(object obj):
    cdef void ** base=NULL
    cdef Py_ssize_t *s=NULL
    return buffers.asbuffer_r(obj, base, s)

def asbuffer_w(object obj):
    cdef void ** base=NULL
    cdef Py_ssize_t *s=NULL
    return buffers.asbuffer_w(obj, base, s)

def newstyle_available():
    return buffers.newstyle_available()
    
def oldstyle_available():
    return buffers.oldstyle_available()

def memoryview_available():
    return buffers.memoryview_available()






