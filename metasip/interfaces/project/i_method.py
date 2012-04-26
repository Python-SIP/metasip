# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.model import Bool, Str

from .i_class_callable import IClassCallable
from .i_doc_string import IDocString
from .i_extended_access import IExtendedAccess


class IMethod(IClassCallable, IDocString, IExtendedAccess):

    abstract = Bool(False)

    const = Bool(False)

    static = Bool(False)

    virtcode = Str()

    virtual = Bool(False)
