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


from ..annos import Annos
from ..code import Code
from ..code_container import CodeContainer
from ..enum import Enum
from ..function import Function
from ..klass import Class
from ..manual_code import ManualCode
from ..namespace import Namespace
from ..opaque_class import OpaqueClass
from ..operator_function import OperatorFunction
from ..typedef import Typedef
from ..variable import Variable

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class NamespaceAdapter(BaseApiAdapter):
    """ This is the Namespace adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'name': AttributeType.STRING,
    }

    # The map of element tags and Code sub-class factories.
    _TAG_CODE_MAP = {
        'Class':            Class,
        'Enum':             Enum,
        'Function':         Function,
        'ManualCode':       ManualCode,
        'Namespace':        Namespace,
        'OpaqueClass':      OpaqueClass,
        'OperatorFunction': OperatorFunction,
        'Typedef':          Typedef,
        'Variable':         Variable,
    }

    def as_str(self):
        """ Return the standard string representation. """

        namespace = self.model

        return 'namespace ' + namespace.name + adapt(namespace, Annos).as_str()

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
