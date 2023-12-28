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
from ..argument import Argument
from ..code import Code

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class CallableAdapter(BaseApiAdapter):
    """ This is the Callable adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'methcode': AttributeType.LITERAL,
        'name':     AttributeType.STRING,
        'pyargs':   AttributeType.STRING,
        'pytype':   AttributeType.STRING,
        'rtype':    AttributeType.STRING,
    }

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
            return_type = self.return_type_as_str()
            args = ', '.join([adapt(arg).as_str() for arg in callable.args])
            s += f' [{return_type} ({args})]'

        return s

    def has_different_signatures(self):
        """ Returns True if the Python and C/C++ signatures are different. """

        callable = self.model

        if callable.pytype != '' or callable.pyargs != '':
            return True

        for arg in callable.args:
            if arg.pytype != '' or arg.pydefault != '':
                return True

        return False

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        # TODO

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Code).load(element, ui)

        for subelement in element:
            if subelement.tag == 'Argument':
                arg = Argument()
                adapt(arg).load(subelement, ui)
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

        for argument in self.model.args:
            adapt(argument).save(output)

        self.save_literal('methcode', output)
