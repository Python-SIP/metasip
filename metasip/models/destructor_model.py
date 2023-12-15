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


from ..dip.model import Bool, Instance, Str

from .access_mixin import AccessMixin
from .class_model import ClassModel
from .code_model import CodeModel


class DestructorModel(CodeModel, AccessMixin):
    """ This class implements a C++ destructor. """

    # The containing class.
    container = Instance(ClassModel)

    # The optional %MethodCode.
    methcode = Str()

    # The name of the destructor.
    # FIXME: Remove this.
    name = Str()

    # The optional %VirtualCatcherCode.
    virtcode = Str()

    # This is set if the destructor is virtual.
    virtual = Bool(False)
