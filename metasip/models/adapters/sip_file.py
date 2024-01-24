# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
from .base_adapter import AttributeType, BaseAdapter


class SipFileAdapter(BaseAdapter):
    """ This is the SipFile adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'exportedheadercode':   AttributeType.LITERAL,
        'exportedtypehintcode': AttributeType.LITERAL,
        'initcode':             AttributeType.LITERAL,
        'modulecode':           AttributeType.LITERAL,
        'moduleheadercode':     AttributeType.LITERAL,
        'name':                 AttributeType.STRING,
        'postinitcode':         AttributeType.LITERAL,
        'preinitcode':          AttributeType.LITERAL,
        'typehintcode':         AttributeType.LITERAL,
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

        return self.model.name

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, CodeContainer).load(self._TAG_CODE_MAP, element,
                project, ui)

        # Progress any UI for the load.
        if ui is not None:
            ui.load_step()

    def save(self, output):
        """ Save the model to an output file. """

        sip_file = self.model

        output.write(f'<SipFile name="{sip_file.name}"')
        adapt(sip_file, CodeContainer).save_attributes(output)
        output.write('>\n')

        output += 1
        adapt(sip_file, CodeContainer).save_subelements(output)
        self.save_literal('exportedheadercode', output)
        self.save_literal('moduleheadercode', output)
        self.save_literal('modulecode', output)
        self.save_literal('preinitcode', output)
        self.save_literal('initcode', output)
        self.save_literal('postinitcode', output)
        self.save_literal('exportedtypehintcode', output)
        self.save_literal('typehintcode', output)
        output -= 1

        output.write('</SipFile>\n')
