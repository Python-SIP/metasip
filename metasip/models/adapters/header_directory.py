# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import os
import sys

from ...helpers import get_platform_name, get_supported_platforms

from ..header_file import HeaderFile
from ..platform import Platform

from .adapt import adapt
from .base_adapter import AttributeType, BaseAdapter


class HeaderDirectoryAdapter(BaseAdapter):
    """ This is the HeaderDirectory adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'name':             AttributeType.STRING,
    }

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        header_directory = self.model

        scan = element.get('scan')
        if scan is None:
            scan = []
        elif scan == '':
            scan = ['']
        else:
            scan = scan.split()

        header_directory.scan = scan

        # Platforms were introduced in project format v0.17.
        if project.version < (0, 17):
            # Create a Platform for legacy versions.
            filefilter = element.get('filefilter')
            inputdirsuffix = element.get('inputdirsuffix')
            parserargs = element.get('parserargs')

            inputdirpattern = os.path.join(inputdirsuffix, filefilter)

            # The C++ standard was hardcoded (so we enforce it here) but should
            # be configurable.
            parserargs = '-std=c++17 ' + parserargs

            header_directory.platforms.append(
                    Platform(name=get_platform_name(),
                            inputdirpattern=inputdirpattern,
                            parserargs=parserargs))

        for subelement in element:
            if subelement.tag == 'HeaderFile':
                header_file = HeaderFile()
                adapt(header_file).load(subelement, project, ui)
                header_directory.content.append(header_file)
            elif subelement.tag == 'Platform':
                platform = Platform()
                adapt(platform).load(subelement, project, ui)
                header_directory.platforms.append(platform)

        # Supply defaults for any missing supported platforms but don't mark
        # the project as dirty so they are only saved if something else has
        # changed.
        platform_names = [p.name for p in header_directory.platforms]

        for supported in get_supported_platforms():
            if supported not in platform_names:
                # On macOS we assume the library being wrapped is a framework.
                if supported == 'macOS':
                    inputdirpattern = header_directory.name + '.framework/Header/*.h'
                    parserargs = '-F .'
                else:
                    inputdirpattern = '*.h'
                    parserargs = ''

                header_directory.platforms.append(
                        Platform(name=supported,
                                inputdirpattern=inputdirpattern,
                                parserargs=parserargs))

    def save(self, output):
        """ Save the model to an output file. """

        header_directory = self.model

        output.write(f'<HeaderDirectory name="{header_directory.name}"')

        if header_directory.scan:
            if header_directory.scan[0] == '':
                scan = ''
            else:
                scan = ' '.join(header_directory.scan)

            self.save_attribute('scan', scan, output)

        output.write('>\n')

        output += 1

        for platform in header_directory.platforms:
            adapt(platform).save(output)

        for header_file in header_directory.content:
            adapt(header_file).save(output)

        output -= 1
        output.write('</HeaderDirectory>\n')
