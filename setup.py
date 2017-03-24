# Copyright (c) 2017 Riverbank Computing Limited.
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
from setuptools import find_packages, setup


# Get the version number.
version_file_name = os.path.join('metasip', 'version.py')
try:
    version_file = open(version_file_name)
    version = version_file.read().strip().split('\n')[0].split()[-1][1:-1]
    version_file.close()
except FileNotFoundError:
    # Provide a minimal version file.
    version = '0.0.dev0'
    version_file = open(version_file_name, 'w')
    version_file.write( 'METASIP_RELEASE = \'%s\'\nMETASIP_HEXVERSION = 0\n' % version)
    version_file.close()


setup(
        name='metasip',
        version=version,
        description='GUI Development Tool for SIP',
        author='Riverbank Computing Limited',
        author_email='info@riverbankcomputing.com',
        url='https://www.riverbankcomputing.com/software/metasip/',
        license='GPL3',
        packages=find_packages(),
        entry_points={
            'console_scripts':  ['msipgen = metasip.main:msipgen_main'],
            'gui_scripts':      ['msip = metasip.main:msip_main']
        }
     )
