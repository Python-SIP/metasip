# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .code import Code
from .code_container import CodeContainer


@dataclass
class Namespace(Code, CodeContainer):
    """ This class implements a namespace. """

    # The name of the namespace.
    name: str = ''

    # The optional %TypeHeaderCode.
    typeheadercode: str = ''
