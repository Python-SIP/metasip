# Copyright (c) 2016 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


import os
from setuptools import setup


# Get the list of packages to include.
packages = []

for dirpath, dirs, files in os.walk('metasip'):
    if '__init__.py' in files:
        packages.append('.'.join(dirpath.split(os.sep)))
    else:
        del dirs[:]


# Get the version number.
version_file = open('VERSION')
version = version_file.read().strip()
version_file.close()


setup(
        name='metasip',
        version=version,
        description='GUI Development Tool for SIP',
        author='Riverbank Computing Limited',
        author_email='info@riverbankcomputing.com',
        url='http://www.riverbankcomputing.com/software/metasip/',
        entry_points={'gui_scripts': ['msip = metasip.main_gui:main']},
        packages=packages
     )
