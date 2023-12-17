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


from ..access import Access
from ..docstring import Docstring
from ..klass import Class
from ..code import Code
from ..code_container import CodeContainer
from ..enum import Enum
from ..manual_code import ManualCode
from ..namespace import Namespace
from ..opaque_class import OpaqueClass
from ..typedef import Typedef
from ..variable import Variable

from .adapt import adapt
from .base_adapter import AttributeType, BaseAdapter


class ClassAdapter(BaseAdapter):
    """ This is the Class adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'bases':    AttributeType.STRING,
        'name':     AttributeType.STRING,
        'pybases':  AttributeType.STRING,
        'struct':   AttributeType.BOOL_FALSE,
    }

    # The map of element tags and Code sub-class factories.
    _TAG_CODE_MAP = {
        'Class':            Class,
        'Enum':             Enum,
        'ManualCode':       ManualCode,
        'Namespace':        Namespace,
        'OpaqueClass':      OpaqueClass,
        'Typedef':          Typedef,
        'Variable':         Variable,
    }

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Code).load(element, ui)
        adapt(self.model, CodeContainer).load(self._TAG_CODE_MAP, element, ui)
        adapt(self.model, Docstring).load(element, ui)
        adapt(self.model, Access).load(element, ui)

        self.set_all_literals(element)
