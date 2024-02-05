# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from abc import ABC, abstractmethod
from enum import auto, Enum
from xml.sax.saxutils import escape

from ...helpers import version_range

from .adapt import adapt


class AttributeType(Enum):
    """ The different types of element and model attributes. """

    BOOL = auto()
    LITERAL = auto()
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

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        # This method must be reimplemented by those adapters that contribute
        # to the comparison of two APIs.  However we don't want to make it
        # abstract and have to provide a stub reimplementation in other
        # adapters.
        raise NotImplementedError

    def as_str(self):
        """ Return the standard string representation. """

        print("!!!", type(self))
        # This method must be reimplemented by those adapters that contribute
        # to the string representation of an API.  However we don't want to
        # make it abstract and have to provide a stub reimplementation in other
        # adapters.
        raise NotImplementedError

    @classmethod
    def expand_type(cls, type, name=None):
        """ Return the full type with an optional name. """

        # Handle the trivial case.
        if type == '':
            return ''

        # This is entirely cosmetic to be consistent with older versions.
        type = cls._normalise_templates(type)

        # SIP can't yet handle every C++ fundamental type.
        s = type.replace('long int', 'long')

        # If there is no embedded %s then just append the name.
        if '%s' in s:
            s = s % name
        elif name:
            if s[-1] not in '&*':
                s += ' '

            s += name

        return s

    def generate_sip_directives(self, output):
        """ Write any directives to a .sip file. """

        # This default implementation does nothing.
        pass

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        # This default implementation loads attributes define by
        # ATTRIBUTE_TYPE_MAP.
        for name, attribute_type in self.ATTRIBUTE_TYPE_MAP.items():
            if attribute_type is AttributeType.BOOL:
                value = bool(int(element.get(name, '0')))
            elif attribute_type is AttributeType.LITERAL:
                for subelement in element:
                    if subelement.tag == 'Literal' and subelement.get('type') == name:
                        value = subelement.text.strip()
                        break
                else:
                    value = ''
            elif attribute_type is AttributeType.STRING:
                value = element.get(name, '')
            elif attribute_type is AttributeType.STRING_LIST:
                value = element.get(name, '').split()

            setattr(self.model, name, value)

    def save(self, output):
        """ Save the model to an output file. """

        # This method must be reimplemented by those adapters that write their
        # own XML element.  However we don't want to make it abstract and have
        # to provide a stub reimplementation in other adapters.
        raise NotImplementedError

    @classmethod
    def save_attribute(cls, name, value, output):
        """ Save an attribute. """

        output.write(f' {name}="{cls._escape(value)}"')

    def save_attributes(self, output):
        """ Save the XML attributes of an adapter that does not write its own
        XML element.
        """

        # This default implementation assumes there are no attributes.
        pass

    def save_bool(self, name, output):
        """ Save a bool. """

        value = getattr(self.model, name)

        if value:
            self.save_attribute(name, '1', output)

    def save_literal(self, name, output):
        """ Save the value of a literal text attribute. """

        value = getattr(self.model, name)

        if value != '':
            output.write(f'<Literal type="{name}">\n{self._escape(value)}\n</Literal>\n', indent=False)

    def save_str(self, name, output):
        """ Save a string. """

        value = getattr(self.model, name)

        if value != '':
            self.save_attribute(name, value, output)

    def save_str_list(self, name, output):
        """ Save a list of strings. """

        value = getattr(self.model, name)

        if len(value) != 0:
            self.save_attribute(name, ' '.join(value), output)

    def save_subelements(self, output):
        """ Save the XML subelements of an adapter that does not write its own
        XML element.
        """

        # This default implementation assumes there are no subelements.
        pass

    @staticmethod
    def _escape(s):
        """ Return an XML escaped string. """

        return escape(s, {'"': '&quot;'})

    @classmethod
    def _normalise_templates(cls, type):
        """ Return the normalised form of any templates. """

        t_start = type.find('<')
        t_end = type.rfind('>')

        if t_start > 0 and t_end > t_start:
            xt = []

            # Note that this doesn't handle nested template arguments properly.
            for t_arg in type[t_start + 1:t_end].split(','):
                xt.append(cls._normalise_templates(t_arg.strip()))

            type = type[:t_start + 1] + ', '.join(xt) + type[t_end:]

        return type


class BaseApiAdapter(BaseAdapter):
    """ This is the base class for all adapters for models that are written to
    a .sip file and provide a user-friendly, one line string representation.
    """

    @abstractmethod
    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        ...

    def version_start(self, output):
        """ Write the start of the version tests for an API.  Returns the
        number of %End statements needed to be passed to the corresponding call
        to version_end().
        """

        api = self.model

        nr_ends = 0

        for vrange in api.versions:
            vr = version_range(vrange)
            output.write(f'%If ({vr})\n', indent=False)
            nr_ends += 1

        # Multiple platforms are logically or-ed.
        if len(api.platforms) != 0:
            platforms = ' || '.join(api.platforms)
            output.write(f'%If ({platforms})\n', indent=False)
            nr_ends += 1

        # Multiple features are nested (ie. logically and-ed).
        for feature in api.features:
            output.write(f'%If ({feature})\n', indent=False)
            nr_ends += 1

        # Also handle comments.
        if api.comments != '':
            for line in api.comments.split('\n'):
                line = line.rstrip()
                if line != '':
                    line = '// ' + line + '\n'
                else:
                    line = '//\n'

                output.write(line)

        return nr_ends

    @staticmethod
    def version_end(nr_ends, output):
        """ Write the end of the version tests for an API item. """

        for _ in range(nr_ends):
            output.write('%End\n', indent=False)
