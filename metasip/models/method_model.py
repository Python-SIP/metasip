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

from .class_callable_model import ClassCallableModel
from .docstring_mixin import DocstringMixin
from .extended_access_mixin import ExtendedAccessMixin


class MethodModel(ClassCallableModel, DocstringMixin, ExtendedAccessMixin):
    """ This class implements a C++ class method. """

    # This is set if the method is abstract.
    abstract = Bool(False)

    # This is set if the method is const.
    const = Bool(False)

    # This is set if the method is final.
    final = Bool(False)

    # This is set if the method is static.
    static = Bool(False)

    # The optional %VirtualCatcherCode.
    virtcode = Str()

    # This is set if the method is virtual.
    virtual = Bool(False)
