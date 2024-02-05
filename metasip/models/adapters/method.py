# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..annos import Annos
from ..callable import Callable
from ..docstring import Docstring
from ..extended_access import ExtendedAccess

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class MethodAdapter(BaseApiAdapter):
    """ This is the Method adapter. """

    ATTRIBUTE_TYPE_MAP = {
        'abstract': AttributeType.BOOL,
        'const':    AttributeType.BOOL,
        'final':    AttributeType.BOOL,
        'static':   AttributeType.BOOL,
        'virtcode': AttributeType.LITERAL,
        'virtual':  AttributeType.BOOL,
    }

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        method = self.model
        other_method = other.model

        if type(method) is not type(other_method):
            return False

        if adapt(method, Callable) != adapt(other_method, Callable):
            return False

        # This code is called when we are comparing a potentially new version
        # of an API item (when the extended access hasn't been specified yet)
        # with an existing one (when the extended access has been specified).
        # Therefore we ignore the extension when doing the comparison.
        access = method.access.replace('signals', '').replace(' slots', '').replace('public', '')
        other_access = other_method.access.replace('signals', '').replace(' slots', '').replace('public', '')
        if access != other_access:
            return False

        # Note that we don't include 'final' because this is implemented as an
        # annotation (because it isn't handled by Cast-XML) and so would always
        # cause a comparison to fail.

        if method.virtual != other_method.virtual:
            return False

        if method.static != other_method.static:
            return False

        if method.const != other_method.const:
            return False

        if method.abstract != other_method.abstract:
            return False

        return True

    def as_str(self):
        """ Return the standard string representation. """

        # We can't use the super class version because we might need to stick
        # some text in the middle of it.

        method = self.model

        callable_adapter = adapt(method, Callable)

        s = ''

        if method.virtual:
            s += 'virtual '

        if method.static:
            s += 'static '

        s += callable_adapter.return_type_as_str(allow_py=True) + method.name

        if method.pyargs != '':
            s += method.pyargs
        else:
            args = ', '.join([adapt(arg).as_py_str() for arg in method.args])
            s += '(' + args + ')'

        if method.const:
            s += ' const'

        if method.final:
            s += ' final'

        if method.abstract:
            s += ' = 0'

        s += adapt(method, Annos).as_str()

        if (method.virtual or method.access.startswith('protected') or method.methcode == '') and callable_adapter.has_different_signatures():
            return_type = callable_adapter.return_type_as_str().strip()
            args = ', '.join([adapt(arg).as_str() for arg in method.args])
            s += f' [{return_type} ({args})]'

        return s

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        method = self.model

        nr_ends = self.version_start(output)

        output.write(self.as_str())
        output.write(';\n')

        adapt(method, Docstring).generate_sip_directives(output)
        adapt(method, Callable).generate_sip_directives(output)
        adapt(method, ExtendedAccess).generate_sip_directives(output)
        output.write_code_directive('%VirtualCatcherCode', method.virtcode)

        self.version_end(nr_ends, output)

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, Callable).load(element, project, ui)
        adapt(self.model, Docstring).load(element, project, ui)
        adapt(self.model, ExtendedAccess).load(element, project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        method = self.model

        output.write('<Method')
        adapt(method, Callable).save_attributes(output)
        adapt(method, Docstring).save_attributes(output)
        adapt(method, ExtendedAccess).save_attributes(output)
        self.save_bool('virtual', output)
        self.save_bool('const', output)
        self.save_bool('final', output)
        self.save_bool('static', output)
        self.save_bool('abstract', output)
        output.write('>\n')

        output += 1
        adapt(method, Callable).save_subelements(output)
        adapt(method, Docstring).save_subelements(output)
        adapt(method, ExtendedAccess).save_subelements(output)
        self.save_literal('virtcode', output)
        output -= 1

        output.write('</Method>\n')
