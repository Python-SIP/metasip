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


from ..dip.model import Bool

from .access_mixin import AccessMixin
from .class_callable_model import ClassCallableModel


class OperatorCastModel(ClassCallableModel, AccessMixin):
    """ This class implements a cast operator. """

    # This is set if the operator is const.
    const = Bool(False)
