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
    load and save a modle to a project file and to provide a user-friendly, one
    line string representation.
    """
    # TODO: add IOAdapter and move load() to it.
    # TODO: rename this class as DisplayAdapter as IOAdapter sub-class that
    # adds as_str() and eventually as_sip() (so better name?)
    # OR
    # TODO: move as_str() to DisplayAdapter mixin and also add GeneratorAdapter
    # mixin containing as_sip()
    # Strictly speaking have separate adapters (Load, Save, Display, Generate)
    # as Display and Save only needed by GUI.

    # The default attribute type map.
    ATTRIBUTE_TYPE_MAP = {}

    def __init__(self, model):
        """ Initialise the adapter. """

        self.model = model

    @abstractmethod
    def as_str(self, project):
        """ Return the standard string representation. """

        ...

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

    @classmethod
    def expand_type(cls, type, name=None, project=None):
        """ Return the full type with an optional name. """

        # Handle the trivial case.
        if type == '':
            return ''

        if project is not None:
            const = 'const '
            if type.startswith(const):
                type = type[len(const):]
            else:
                const = ''

            type = const + cls.ignore_namespaces(type, project)

        # SIP can't handle every C++ fundamental type.
        # TODO: add the SIP support.
        type = type.replace('long int', 'long')

        # Append any name.
        s = type

        if name:
            if type[-1] not in '&*':
                s += ' '

            s += name

        return s

    @classmethod
    def ignore_namespaces(cls, type, project):
        """ Return a type with any namespaces to be ignored removed. """

        for ignored_namespace in project.ignorednamespaces:
            namespace_prefix = ignored_namespace + '::'

            if type.startswith(namespace_prefix):
                type = type[len(namespace_prefix):]
                break

        # Handle any template arguments.
        t_start = type.find('<')
        t_end = type.rfind('>')

        if t_start > 0 and t_end > t_start:
            t_args = []

            # Note that this doesn't handle nested template arguments properly.
            for t_arg in type[t_start + 1:t_end].split(','):
                t_args.append(cls.ignore_namespaces(t_arg.strip(), project))

            type = type[:t_start + 1] + ', '.join(t_args) + type[t_end:]

        return type
