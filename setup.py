#!/usr/bin/env python

#
#    Copyright (c) 2010 Brian E. Granger
#
#    This file is part of pyzmq.
#
#    pyzmq is free software; you can redistribute it and/or modify it under
#    the terms of the Lesser GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    pyzmq is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    Lesser GNU General Public License for more details.
#
#    You should have received a copy of the Lesser GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os, sys

try:
    import setuptools
except ImportError:
    pass

from distutils.core import setup, Command
from distutils.extension import Extension
from distutils.command.sdist import sdist

from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin

try:
    from os.path import walk
except:
    from os import walk

from zmq import get_includes

#-----------------------------------------------------------------------------
# Flags
#-----------------------------------------------------------------------------
# ignore unused-function and strict-aliasing warnings, of which there
# will be many from the Cython generated code:
ignore_common_warnings=True

release = False # flag for whether to include *.c in package_data

#-----------------------------------------------------------------------------
# Extra commands
#-----------------------------------------------------------------------------

class TestCommand(Command):
    """Custom distutils command to run the test suite."""

    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        """Finds all the tests modules in zmq/tests/, and runs them."""
        testfiles = [ ]
        for t in glob(pjoin(self._dir, 'checkbuffers', 'tests', '*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(
                    ['checkbuffers.tests', splitext(basename(t))[0]])
                )
        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity = 1)
        t.run(tests)


class CleanCommand(Command):
    """Custom distutils command to clean the .so and .pyc files."""

    user_options = [ ]

    def initialize_options(self):
        self._clean_me = []
        for root, dirs, files in os.walk('.'):
            for f in files:
                if f.endswith('.pyc') or f.endswith('.so'):
                    self._clean_me.append(pjoin(root, f))

    def finalize_options(self):
        pass

    def run(self):
        for clean_me in self._clean_me:
            try:
                os.unlink(clean_me)
            except:
                pass


class CheckSDist(sdist):
    """Custom sdist that ensures Cython has compiled all pyx files to c."""

    def initialize_options(self):
        sdist.initialize_options(self)
        self._pyxfiles = []
        for root, dirs, files in os.walk('.'):
            for f in files:
                if f.endswith('.pyx'):
                    self._pyxfiles.append(pjoin(root, f))
    def run(self):
        for pyxfile in self._pyxfiles:
            cfile = pyxfile[:-3]+'c'
            msg = "C-source file '%s' not found."%(cfile)+\
            " Run 'setup.py cython' before sdist."
            assert os.path.isfile(cfile), msg
        sdist.run(self)

#-----------------------------------------------------------------------------
# Suppress Common warnings
#-----------------------------------------------------------------------------

extra_flags = []
if ignore_common_warnings:
    for warning in ('unused-function', 'strict-aliasing'):
        extra_flags.append('-Wno-'+warning)

#-----------------------------------------------------------------------------
# Extensions
#-----------------------------------------------------------------------------

cmdclass = {'test':TestCommand, 'clean':CleanCommand }

includes = [ inc for inc in get_includes() if 'utils' in inc ]

def pxd(subdir, name):
    return os.path.abspath(pjoin('checkbuffers', subdir, name+'.pxd'))

def pyx(subdir, name):
    return os.path.abspath(pjoin('checkbuffers', subdir, name+'.pyx'))

def dotc(subdir, name):
    return os.path.abspath(pjoin('checkbuffers', subdir, name+'.c'))


try:
    from Cython.Distutils import build_ext
except ImportError:
    suffix = '.c'
else:
    
    suffix = '.pyx'
    
    class CythonCommand(build_ext):
        """Custom distutils command subclassed from Cython.Distutils.build_ext
        to compile pyx->c, and stop there. All this does is override the 
        C-compile method build_extension() with a no-op."""
        def build_extension(self, ext):
            pass
    
    cmdclass['cython'] = CythonCommand
    cmdclass['build_ext'] =  build_ext
    cmdclass['sdist'] =  CheckSDist

extensions = []

sources = [pjoin('checkbuffers', 'checkbuffers'+suffix)]
ext = Extension(
    'checkbuffers.checkbuffers',
    sources = sources,
    libraries = [],
    include_dirs = includes,
    extra_compile_args = extra_flags
)
extensions.append(ext)

#
package_data = {}

if release:
    for pkg,data in pkgdata.iteritems():
        data.append('*.c')
        
#-----------------------------------------------------------------------------
# Main setup
#-----------------------------------------------------------------------------

long_desc = \
"""
PyZMQ is a lightweight and super-fast messaging library built on top of
the ZeroMQ library (http://www.zeromq.org). 
"""

setup(
    name = "checkbuffers",
    version = "2.0.9dev",
    packages = ['checkbuffers'],
    ext_modules = extensions,
    package_data = package_data,
    author = "Min Ragan-Kelley",
    author_email = "benjaminrk@gmail.com",
    url = 'http://github.com/minrk/checkbuffers',
    download_url = 'http://github.com/minrk/checkbuffers/downloads',
    description = "checking utility for pyzmq buffers.pxd file",
    long_description = long_desc, 
    license = "BSD",
    cmdclass = cmdclass,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Berkeley Software Distribution License (BSD)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Bug Tracking'
    ]
)

