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


from ..header_file import HeaderFile

from .adapt import adapt
from .base_adapter import AttributeType, BaseAdapter


class HeaderDirectoryAdapter(BaseAdapter):
    """ This is the HeaderDirectory adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'filefilter':       AttributeType.STRING,
        'inputdirsuffix':   AttributeType.STRING,
        'name':             AttributeType.STRING,
        'parserargs':       AttributeType.STRING,
    }

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        scan = element.get('scan')
        if scan is None:
            scan = []
        elif scan == '':
            scan = ['']
        else:
            scan = scan.split()

        self.model.scan = scan

        for subelement in element:
            if subelement.tag == 'HeaderFile':
                header_file = HeaderFile()
                adapt(header_file).load(subelement, ui)
                self.model.content.append(header_file)
