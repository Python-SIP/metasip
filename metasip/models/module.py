# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
    # TODO: remove this and use the module name instead.
    outputdirsuffix: str = ''

    # Set if the module is PY_SSIZE_T_CLEAN.
    pyssizetclean: bool = False

    # Set if the limited Python API should be used.
    uselimitedapi: bool = False

    # The default virtual error handler.
    virtualerrorhandler: str = ''
