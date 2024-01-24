# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..header_directory import HeaderDirectory
from ..module import Module
from ..project_version import ProjectVersion

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

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        # Initialise any UI for the load.
        if ui is not None:
            # Each .sip file is a step of the load.
            ui.load_starting(self.model, len(element.findall('.//SipFile')))

        super().load(element, project, ui)

        for subelement in element:
            if subelement.tag == 'HeaderDirectory':
                header_directory = HeaderDirectory()
                adapt(header_directory).load(subelement, project, ui)
                self.model.headers.append(header_directory)
            elif subelement.tag == 'Module':
                module = Module()
                adapt(module).load(subelement, project, ui)
                self.model.modules.append(module)

    def save(self, output):
        """ Save the model to an output file. """

        project = self.model

        # Note that we always use the current project version.
        major_version, minor_version = ProjectVersion
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
