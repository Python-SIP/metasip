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
from .class_callable_model import ClassCallableModel


class OperatorMethodModel(ClassCallableModel, AccessMixin):
    """ This class implements a C++ class operator. """

    # This is set if the operator is abstract.
    abstract = Bool(False)

    # This is set if the operator is const.
    const = Bool(False)

    # The optional %VirtualCatcherCode.
    virtcode = Str()

    # This is set if the operator is virtual.
    virtual = Bool(False)
