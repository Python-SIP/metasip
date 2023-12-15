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


from ..dip.model import Bool, Str

from .access_mixin import AccessMixin
from .code_model import CodeModel


class VariableModel(CodeModel, AccessMixin):
    """ This class implements C struct and C++ class member variables. """

    # The optional %AccessCode.
    accesscode = Str()

    # The optional %GetCode.
    getcode = Str()

    # The name of the variable.
    name = Str()

    # The optional %SetCode.
    setcode = Str()

    # This is set if the variable is static.
    static = Bool(False)

    # The type of the variable.
    type = Str()
