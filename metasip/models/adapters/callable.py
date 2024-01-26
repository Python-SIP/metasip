# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..annos import Annos
from ..argument import Argument
from ..code import Code

from .adapt import adapt
from .base_adapter import AttributeType, BaseAdapter


class CallableAdapter(BaseAdapter):
    """ This is the Callable adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'methcode': AttributeType.LITERAL,
        'name':     AttributeType.STRING,
        'pyargs':   AttributeType.STRING,
        'pytype':   AttributeType.STRING,
        'rtype':    AttributeType.STRING,
    }

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        callable = self.model
        other_callable = other.model

        # Note that we have already checked the types.

        if callable.name != other_callable.name:
            return False

        if self.expand_type(callable.rtype) != self.expand_type(other_callable.rtype):
            return False

        if len(callable.args) != len(other_callable.args):
            return False

        for arg, other_arg in zip(callable.args, other_callable.args):
            if adapt(arg) != adapt(other_arg):
                return False

        return True

    def as_str(self):
        """ Return the standard string representation. """

        callable = self.model

        # This is the Python signature.
        s = self.return_type_as_str(allow_py=True) + callable.name

        if callable.pyargs != '':
            s += callable.pyargs
        else:
            args = ', '.join([adapt(arg).as_py_str() for arg in callable.args])
            s += '(' + args + ')'

        s += adapt(callable, Annos).as_str()

        # We include a separate C++ signature if it is different to the Python
        # signature.  This is so we always hint to the user that something has
        # been manually changed.
        if self.has_different_signatures():
            return_type = self.return_type_as_str().strip()
            if return_type != '':
                return_type += ' '

            args = ', '.join([adapt(arg).as_str() for arg in callable.args])
            s += f' [{return_type}({args})]'

        return s

    def has_different_signatures(self):
        """ Returns True if the Python and C/C++ signatures are different. """

        callable = self.model

        if callable.pytype != '' or callable.pyargs != '':
            return True

        for arg in callable.args:
            if arg.pytype != '':
                return True

        return False

    def generate_sip_directives(self, output):
        """ Write any directives to a .sip file. """

        output.write_code_directive('%MethodCode', self.model.methcode)

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, Code).load(element, project, ui)

        for subelement in element:
            if subelement.tag == 'Argument':
                arg = Argument()
                adapt(arg).load(subelement, project, ui)
                self.model.args.append(arg)

    def return_type_as_str(self, allow_py=False):
        """ Return the return type as a string. """

        callable = self.model

        if callable.pytype != '' and allow_py:
            s = callable.pytype
        elif callable.rtype != '':
            s = self.expand_type(callable.rtype)
        else:
            return ''

        if s[-1] not in '&*':
            s += ' '

        return s

    def save_attributes(self, output):
        """ Save the XML attributes. """

        callable = self.model

        adapt(callable, Code).save_attributes(output)
        self.save_attribute('name', callable.name, output)
        self.save_str('rtype', output)
        self.save_str('pytype', output)
        self.save_str('pyargs', output)

    def save_subelements(self, output):
        """ Save the XML subelements. """

        adapt(self.model, Code).save_subelements(output)

        for argument in self.model.args:
            adapt(argument).save(output)

        self.save_literal('methcode', output)
