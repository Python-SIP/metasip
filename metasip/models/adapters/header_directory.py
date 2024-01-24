# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

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
                adapt(header_file).load(subelement, project, ui)
                self.model.content.append(header_file)

    def save(self, output):
        """ Save the model to an output file. """

        header_directory = self.model

        output.write(f'<HeaderDirectory name="{header_directory.name}" parserargs="{header_directory.parserargs}" inputdirsuffix="{header_directory.inputdirsuffix}" filefilter="{header_directory.filefilter}"')

        if len(header_directory.scan) != 0:
            if header_directory.scan[0] == '':
                scan = ''
            else:
                scan = ' '.join(header_directory.scan)

            self.save_attribute('scan', scan, output)

        output.write('>\n')

        output += 1

        for header_file in header_directory.content:
            adapt(header_file).save(output)

        output -= 1
        output.write('</HeaderDirectory>\n')
