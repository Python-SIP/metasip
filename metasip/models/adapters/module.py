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


from ..sip_file import SipFile

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class ModuleAdapter(BaseApiAdapter):
    """ This is the Module adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'directives':           AttributeType.LITERAL,
        'imports':              AttributeType.STRING_LIST,
        'name':                 AttributeType.STRING,
        'outputdirsuffix':      AttributeType.STRING,
        'pyssizetclean':        AttributeType.BOOL,
        'uselimitedapi':        AttributeType.BOOL,
        'virtualerrorhandler':  AttributeType.STRING,
    }

    def as_str(self):
        """ Return the standard string representation. """

        return self.model.name

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        # TODO

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        callsuperinit = int(element.get('callsuperinit', '-1'))
        if callsuperinit < 0:
            callsuperinit = 'undefined'
        elif callsuperinit == 0:
            callsuperinit = 'no'
        else:
            callsuperinit = 'yes'

        self.model.callsuperinit = callsuperinit

        for subelement in element:
            if subelement.tag == 'SipFile':
                sip_file = SipFile()
                adapt(sip_file).load(subelement, ui)
                self.model.content.append(sip_file)

    def save(self, output):
        """ Save the model to an output file. """

        module = self.model

        output.write(f'<Module name="{module.name}"')
        self.save_str('outputdirsuffix', output)

        if module.callsuperinit != 'undefined':
            self.save_attribute('callsuperinit',
                    '1' if module.callsuperinit == 'yes' else '0', output)

        self.save_str('virtualerrorhandler', output)
        self.save_bool('uselimitedapi', output)
        self.save_bool('pyssizetclean', output)
        self.save_str_list('imports', output)
        output.write('>\n')
        output += 1

        self.save_literal('directives', output)

        for sip_file in module.content:
            adapt(sip_file).save(output)

        output -= 1
        output.write('</Module>\n')
