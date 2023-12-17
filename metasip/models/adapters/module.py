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
from .base_adapter import AttributeType, BaseAdapter


class ModuleAdapter(BaseAdapter):
    """ This is the Module adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'imports':              AttributeType.STRING_LIST,
        'name':                 AttributeType.STRING,
        'outputdirsuffix':      AttributeType.STRING,
        'pyssizetclean':        AttributeType.BOOL_FALSE,
        'uselimitedapi':        AttributeType.BOOL_FALSE,
        'virtualerrorhandler':  AttributeType.STRING,
    }

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
            if subelement.tag == 'Literal':
                self.set_literal(subelement)
            elif subelement.tag == 'SipFile':
                sip_file = SipFile()
                adapt(sip_file).load(subelement, ui)
                self.model.content.append(sip_file)
