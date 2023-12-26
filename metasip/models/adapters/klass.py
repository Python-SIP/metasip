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
from ..annos import Annos
from ..constructor import Constructor
from ..destructor import Destructor
from ..docstring import Docstring
from ..klass import Class
from ..code import Code
from ..code_container import CodeContainer
from ..enum import Enum
from ..manual_code import ManualCode
from ..method import Method
from ..namespace import Namespace
from ..opaque_class import OpaqueClass
from ..operator_cast import OperatorCast
from ..operator_method import OperatorMethod
from ..typedef import Typedef
from ..variable import Variable

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class ClassAdapter(BaseApiAdapter):
    """ This is the Class adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'bases':    AttributeType.STRING,
        'name':     AttributeType.STRING,
        'pybases':  AttributeType.STRING,
        'struct':   AttributeType.BOOL,
    }

    # The map of element tags and Code sub-class factories.
    _TAG_CODE_MAP = {
        'Class':            Class,
        'Constructor':      Constructor,
        'Destructor':       Destructor,
        'Enum':             Enum,
        'ManualCode':       ManualCode,
        'Method':           Method,
        'Namespace':        Namespace,
        'OpaqueClass':      OpaqueClass,
        'OperatorCast':     OperatorCast,
        'OperatorMethod':   OperatorMethod,
        'Typedef':          Typedef,
        'Variable':         Variable,
    }

    def as_str(self):
        """ Return the standard string representation. """

        klass = self.model

        s = 'struct' if klass.struct else 'class'

        if klass.name != '':
            s += ' ' + klass.name

        if klass.bases != '':
            s += ' : ' + klass.bases

        s += adapt(klass, Annos).as_str()

        return s

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        # TODO

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Code).load(element, ui)
        adapt(self.model, CodeContainer).load(self._TAG_CODE_MAP, element, ui)
        adapt(self.model, Docstring).load(element, ui)
        adapt(self.model, Access).load(element, ui)
