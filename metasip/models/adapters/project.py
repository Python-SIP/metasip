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


from ..header_directory import HeaderDirectory
from ..module import Module

from .adapt import adapt
from .base_adapter import AttributeType, BaseAdapter


class ProjectAdapter(BaseAdapter):
    """ This is the Project adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'externalfeatures':     AttributeType.STRING_LIST,
        'externalmodules':      AttributeType.STRING_LIST,
        'features':             AttributeType.STRING_LIST,
        'platforms':            AttributeType.STRING_LIST,
        'rootmodule':           AttributeType.STRING,
        'sipcomments':          AttributeType.LITERAL,
        'versions':             AttributeType.STRING_LIST,
    }

    def as_str(self):
        """ Return the standard string representation. """

        return self.model.rootmodule

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        # Initialise any UI for the load.
        if ui is not None:
            # Each .sip file is a step of the load.
            ui.load_starting(self.model, len(element.findall('.//SipFile')))

        super().load(element, ui)

        for subelement in element:
            if subelement.tag == 'HeaderDirectory':
                header_directory = HeaderDirectory()
                adapt(header_directory).load(subelement, ui)
                self.model.headers.append(header_directory)
            elif subelement.tag == 'Module':
                module = Module()
                adapt(module).load(subelement, ui)
                self.model.modules.append(module)

    def save(self, output):
        """ Save the model to an output file. """

        project = self.model

        major_version, minor_version = project.version
        if major_version == 0:
            format_version = f'version="{minor_version}"'
        else:
            format_version = f'majorversion="{major_version}" minorversion="{minor_version}"'

        output.write('<?xml version="1.0"?>\n')
        output.write(
                f'<Project {format_version} rootmodule="{project.rootmodule}"')
        self.save_str_list('versions', output)
        self.save_str_list('platforms', output)
        self.save_str_list('features', output)
        self.save_str_list('externalmodules', output)
        self.save_str_list('externalfeatures', output)
        output.write('>\n')
        output += 1

        self.save_literal('sipcomments', output)

        for header_directory in project.headers:
            adapt(header_directory).save(output)

        for module in project.modules:
            adapt(module).save(output)

        output -= 1
        output.write('</Project>\n')
