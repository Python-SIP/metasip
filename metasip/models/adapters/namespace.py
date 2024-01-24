# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        namespace = self.model
        other_namespace = other.model

        if type(namespace) is not type(other_namespace):
            return False

        if namespace.name != other_namespace.name:
            return False

        return True

    def as_str(self):
        """ Return the standard string representation. """

        namespace = self.model

        return 'namespace ' + namespace.name + adapt(namespace, Annos).as_str()

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        namespace = self.model

        nr_ends = self.version_start(output)

        output.blank()

        output.write(self.as_str())
        output.write('\n{\n')

        output.write('%TypeHeaderCode\n', indent=False)

        if namespace.typeheadercode != '':
            output.write(namespace.typeheadercode + '\n', indent=False)
        else:
            output.write(f'#include <{sip_file.name}>\n', indent=False)

        output.write('%End\n', indent=False)

        output.blank()

        output += 1

        for api in namespace.content:
            if api.status == '':
                adapt(api).generate_sip(sip_file, output)

        output -= 1

        output.write('};\n')

        output.blank()

        self.version_end(nr_ends, output)

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, Code).load(element, project, ui)
        adapt(self.model, CodeContainer).load(self._TAG_CODE_MAP, element,
                project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        namespace = self.model

        output.write('<Namespace')
        adapt(namespace, Code).save_attributes(output)
        adapt(namespace, CodeContainer).save_attributes(output)
        self.save_attribute('name', namespace.name, output)
        output.write('>\n')

        output += 1
        self.save_literal('typeheadercode', output)
        adapt(namespace, Code).save_subelements(output)
        adapt(namespace, CodeContainer).save_subelements(output)
        output -= 1

        output.write('</Namespace>\n')
