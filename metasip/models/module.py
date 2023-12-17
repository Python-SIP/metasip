# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dataclasses import dataclass, field

from .sip_file import SipFile


@dataclass
class Module:
    """ This class implements a Python module. """

    # Whether instances of classes defined in the module should call
    # super().__init().  Values are 'undefined', 'no' and 'yes'.
    callsuperinit: str = ''

    # The list of .sip files defining API items included in the module.
    content: list[SipFile] = field(default_factory=list)

    # The SIP directives to be included at the start of the main .sip file for
    # the module.
    directives: str = ''

    # The list of modules that this module depends on.
    imports: list[str] = field(default_factory=list)

    # The name of the module.
    name: str = ''

    # The optional suffix added to the output directory to create the full name
    # of the directory where the generated .sip files will be placed.
    outputdirsuffix: str = ''

    # Set if the module is PY_SSIZE_T_CLEAN.
    pyssizetclean: bool = False

    # Set if the limited Python API should be used.
    uselimitedapi: bool = False

    # The default virtual error handler.
    virtualerrorhandler: str = ''
