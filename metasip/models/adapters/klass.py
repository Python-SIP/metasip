# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..access import Access
from ..annos import Annos
from ..constructor import Constructor
from ..destructor import Destructor
from ..docstring import Docstring
from ..extended_access import ExtendedAccess
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
        'bases':            AttributeType.STRING,
        'bicharbufcode':    AttributeType.LITERAL,
        'bigetbufcode':     AttributeType.LITERAL,
        'bireadbufcode':    AttributeType.LITERAL,
        'birelbufcode':     AttributeType.LITERAL,
        'bisegcountcode':   AttributeType.LITERAL,
        'biwritebufcode':   AttributeType.LITERAL,
        'convfromtypecode': AttributeType.LITERAL,
        'convtotypecode':   AttributeType.LITERAL,
        'gcclearcode':      AttributeType.LITERAL,
        'gctraversecode':   AttributeType.LITERAL,
        'name':             AttributeType.STRING,
        'picklecode':       AttributeType.LITERAL,
        'pybases':          AttributeType.STRING,
        'struct':           AttributeType.BOOL,
        'subclasscode':     AttributeType.LITERAL,
        'finalisationcode': AttributeType.LITERAL,
        'typecode':         AttributeType.LITERAL,
        'typeheadercode':   AttributeType.LITERAL,
        'typehintcode':     AttributeType.LITERAL,
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

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        klass = self.model
        other_klass = other.model

        if type(klass) is not type(other_klass):
            return False

        if klass.access != other_klass.access:
            return False

        if klass.name != other_klass.name:
            return False

        if klass.struct != other_klass.struct:
            return False

        if klass.bases != other_klass.bases:
            return False

        return True

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

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        klass = self.model

        nr_ends = self.version_start(output)

        output.blank()

        type_type = 'struct ' if klass.struct else 'class '
        bases_s = ''

        if klass.pybases != '':
            # Treat None as meaning no super classes:
            if klass.pybases != 'None':
                bases_s = ' : ' + ', '.join(klass.pybases.split())
        elif klass.bases != '':
            bases = []

            for base in klass.bases.split(', '):
                access, base_cls = base.split()
                bases.append(f'{access} {base_cls}')

            bases_s = ' : ' + ', '.join(bases)

        output.write(type_type + klass.name + bases_s + adapt(klass, Annos).as_str() + '\n{\n')

        adapt(klass, Docstring).generate_sip_directives(output)
        output.write_code_directive('%TypeHintCode', klass.typehintcode,
                indent=False)

        output.write('%TypeHeaderCode\n', indent=False)

        if klass.typeheadercode != '':
            output.write(klass.typeheadercode + '\n', indent=False)
        else:
            output.write(f'#include <{sip_file.name}>\n', indent=False)

        output.write('%End\n', indent=False)

        output.blank()

        output.write_code_directive('%TypeCode', klass.typecode, indent=False)
        output.write_code_directive('%FinalisationCode',
                klass.finalisationcode)
        output.write_code_directive('%ConvertToSubClassCode',
                klass.subclasscode)
        output.write_code_directive('%ConvertToTypeCode', klass.convtotypecode,
                indent=False)
        output.write_code_directive('%ConvertFromTypeCode',
                klass.convfromtypecode, indent=False)
        output.write_code_directive('%GCTraverseCode', klass.gctraversecode)
        output.write_code_directive('%GCClearCode', klass.gcclearcode)
        output.write_code_directive('%BIGetBufferCode', klass.bigetbufcode)
        output.write_code_directive('%BIReleaseBufferCode', klass.birelbufcode)
        output.write_code_directive('%BIGetReadBufferCode',
                klass.bireadbufcode)
        output.write_code_directive('%BIGetWriteBufferCode',
                klass.biwritebufcode)
        output.write_code_directive('%BIGetSegCountCode', klass.bisegcountcode)
        output.write_code_directive('%BIGetCharBufferCode',
                klass.bicharbufcode)
        output.write_code_directive('%PickleCode', klass.picklecode)

        output += 1

        access = '' if klass.struct else 'private'

        for api in klass.content:
            if api.status != '':
                continue

            if isinstance(api, (Access, ExtendedAccess)):
                if access != api.access:
                    output -= 1
                    access = api.access

                    if access != '':
                        access_s = access
                    else:
                        access_s = 'public'

                    output.blank()
                    output.write(access_s + ':\n')
                    output += 1

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
        adapt(self.model, Docstring).load(element, project, ui)
        adapt(self.model, Access).load(element, project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        klass = self.model

        output.write('<Class')
        adapt(klass, Code).save_attributes(output)
        adapt(klass, CodeContainer).save_attributes(output)
        adapt(klass, Docstring).save_attributes(output)
        adapt(klass, Access).save_attributes(output)
        self.save_attribute('name', klass.name, output)
        self.save_str('bases', output)
        self.save_str('pybases', output)
        self.save_bool('struct', output)
        output.write('>\n')

        output += 1
        # The order is to match older versions.
        adapt(klass, Code).save_subelements(output)
        adapt(klass, Docstring).save_subelements(output)
        self.save_literal('typehintcode', output)
        self.save_literal('typeheadercode', output)
        self.save_literal('typecode', output)
        self.save_literal('finalisationcode', output)
        self.save_literal('subclasscode', output)
        self.save_literal('convtotypecode', output)
        self.save_literal('convfromtypecode', output)
        self.save_literal('gctraversecode', output)
        self.save_literal('gcclearcode', output)
        self.save_literal('bigetbufcode', output)
        self.save_literal('birelbufcode', output)
        self.save_literal('bireadbufcode', output)
        self.save_literal('biwritebufcode', output)
        self.save_literal('bisegcountcode', output)
        self.save_literal('bicharbufcode', output)
        self.save_literal('picklecode', output)
        adapt(klass, CodeContainer).save_subelements(output)
        adapt(klass, Access).save_subelements(output)
        output -= 1

        output.write('</Class>\n')
