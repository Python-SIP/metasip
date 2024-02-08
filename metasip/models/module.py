# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass, field
from typing import List

from .sip_file import SipFile


@dataclass
class Module:
    """ This class implements a Python module. """

    # Whether instances of classes defined in the module should call
    # super().__init().  Values are 'undefined', 'no' and 'yes'.
    callsuperinit: str = ''

    # The list of .sip files defining API items included in the module.
    content: List[SipFile] = field(default_factory=list)

    # The SIP directives to be included at the start of the main .sip file for
    # the module.
    directives: str = ''

    # The list of modules that this module depends on.
    imports: List[str] = field(default_factory=list)

    # The default handling of keyword arguments, either '', 'all' or
    # 'optional'.
    # Added in v0.17
    keywordarguments: str = ''

    # The name of the module.
    name: str = ''

    # The optional suffix added to the output directory to create the full name
    # of the directory where the generated .sip files will be placed.
    # Removed in v0.17
    outputdirsuffix: str = ''

    # Set if the module is PY_SSIZE_T_CLEAN.
    pyssizetclean: bool = False

    # Set if the limited Python API should be used.
    uselimitedapi: bool = False

    # The default virtual error handler.
    virtualerrorhandler: str = ''
