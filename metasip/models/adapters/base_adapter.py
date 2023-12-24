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


from abc import ABC, abstractmethod
from enum import auto, Enum

from .adapt import adapt


class AttributeType(Enum):
    """ The different types of element and model attributes. """

    BOOL_FALSE = auto()
    BOOL_TRUE = auto()
    STRING = auto()
    STRING_LIST = auto()


class BaseAdapter(ABC):
    """ This is the base class for all adapters and provides the ability to
    load and save a model to a project file and to provide a user-friendly, one
    line string representation.
    """

    # The default attribute type map.
    ATTRIBUTE_TYPE_MAP = {}

    def __init__(self, model):
        """ Initialise the adapter. """

        self.model = model

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        # This default implementation loads attributes define by
        # ATTRIBUTE_TYPE_MAP.
        for name, attribute_type in self.ATTRIBUTE_TYPE_MAP.items():
            if attribute_type is AttributeType.BOOL_FALSE:
                value = bool(int(element.get(name, '0')))
            elif attribute_type is AttributeType.BOOL_TRUE:
                value = bool(int(element.get(name, '1')))
            elif attribute_type is AttributeType.STRING:
                value = element.get(name, '')
            elif attribute_type is AttributeType.STRING_LIST:
                value = element.get(name, '').split()

            setattr(self.model, name, value)

    def set_all_literals(self, element):
        """ Set all literal text attributes of the model from an element. """

        for subelement in element:
            if subelement.tag == 'Literal':
                self.set_literal(subelement)

    def set_literal(self, element):
        """ Set a literal text attribute of the model from an element. """

        setattr(self.model, element.get('type'), element.text.strip())


class BaseApiAdapter(BaseAdapter):
    """ This is the base class for all adapters for models that are written to
    a .sip file and provide a user-friendly, one line string representation.
    """

    @abstractmethod
    def as_str(self):
        """ Return the standard string representation. """

        ...

    @staticmethod
    def expand_type(type, name=None):
        """ Return the full type with an optional name. """

        # Handle the trivial case.
        if type == '':
            return ''

        # SIP can't handle every C++ fundamental type.
        # TODO: add the SIP support.
        s = type.replace('long int', 'long')

        # Append any name.
        if name:
            if s[-1] not in '&*':
                s += ' '

            s += name

        return s

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        # This default implementation writes out the strip representation as a
        # complete line.
        output.write_line(self.as_str())
