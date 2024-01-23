# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import os

from ..exceptions import UserException
from ..helpers import VersionMap, version_range
from ..models import Enum, Function, Variable
from ..models.adapters import adapt

from .indent_file import IndentFile


def generate_sip_files(project, output_dir, ignored_modules, verbose):
    """ Generate the .sip files for a project. """

    if ignored_modules is None:
        ignored_modules = []

    for module in project.modules:
        # See if the module should be ignored.
        if module.name in ignored_modules:
            if verbose:
                print(f"Ignoring {module.name}")

            continue

        # Create the module-specific output directory.
        if project.version >= (0, 17):
            module_output_dir = os.path.join(output_dir, module.name)
        else:
            if module.outputdirsuffix != '':
                module_output_dir = os.path.join(output_dir, module.outputdirsuffix)
            else:
                module_output_dir = output_dir

        # Make sure the output directory exists.
        try:
            os.makedirs(module_output_dir)
        except:
            pass

        # Generate .sip files for the module contents.
        sip_file_names = []

        for sip_file in module.content:
            (file_name, _) = os.path.splitext(os.path.basename(sip_file.name))
            file_name += '.sip'
            sip_file_names.append(file_name)

            output = _create_sip_file(project, module, module_output_dir,
                    file_name, verbose)
            _generate_sip(sip_file, project, output)
            output.close()

        # Generate the .sip file defining the module itself.
        output = _create_sip_file(project, module, module_output_dir,
                module.name + 'mod.sip', verbose)

        root_name = project.rootmodule

        if root_name != '':
            root_name += "."

        output.write('%Module(name=' + root_name + module.name)

        if module.callsuperinit != 'undefined':
            output.write(', call_super_init=' + ('True' if module.callsuperinit == 'yes' else 'False'))

        if module.virtualerrorhandler != '':
            output.write(', default_VirtualErrorHandler=' + module.virtualerrorhandler)

        output.write(', keyword_arguments="Optional"')

        if module.uselimitedapi:
            output.write(', use_limited_api=True')

        if module.pyssizetclean:
            output.write(', py_ssize_t_clean=True')

        output.write(')\n\n')

        top_level_module = True

        if len(module.imports) != 0:
            for imported in module.imports:
                output.write(f'%Import {imported}/{imported}mod.sip\n')

                if imported not in project.externalmodules:
                    top_level_module = False

            output.write('\n')

        if top_level_module:
            # Add any version, platform and feature information to all top
            # level modules (ie. those that don't import anything).

            if len(project.versions) != 0:
                versions = ' '.join(project.versions)
                output.write(f'%Timeline {{{versions}}}\n\n')

            if len(project.platforms) != 0:
                platforms = ' '.join(project.platforms)
                output.write(f'%Platforms {{{platforms}}}\n\n')

            if len(project.features) != 0:
                for feature in project.features:
                    output.write(f'%Feature {feature}\n')

                output.write('\n')

        if module.directives != '':
            output.write(module.directives)
            output.write('\n\n')

        for file_name in sip_file_names:
            output.write(f'%Include {file_name}\n')

        output.close()


def _create_sip_file(project, module, module_output_dir, file_name, verbose):
    """ Create and return a boilerplate .sip file. """

    if verbose:
        print(f"Generating '{file_name}'")

    output = _IndentSipFile.create(os.path.join(module_output_dir, file_name))

    # Add the standard header.
    output.write(
f'''// {file_name} generated by MetaSIP
//
// This file is part of the {module.name} Python extension module.
''')

    if project.sipcomments:
        output.write(f'//\n{project.sipcomments}\n')

    output.write('\n')
    output.blank()

    return output


def _generate_sip(sip_file, project, output):
    """ Generate the contents of a .sip file. """

    # See if we need a %ModuleCode directive for things which will be
    # implemented at the module level.  At the same time find the version
    # ranges that cover all the API items.
    vmap = VersionMap(project)
    platforms = set()
    features = set()
    need_header = False

    for api in sip_file.content:
        if api.status != '':
            continue

        # Note that OperatorFunctions are handled within the class even if they
        # have global declarations.
        if isinstance(api, (Enum, Function, Variable)):
            need_header = True

        vmap.update_from_version_ranges(api.versions)

        if platforms is not None:
            if len(api.platforms) != 0:
                platforms.update(api.platforms)
            else:
                platforms = None

        if features is not None:
            if len(api.features) != 0:
                features.update(api.features)
            else:
                features = None

    if need_header:
        vranges_str = [version_range(vr) for vr in vmap.as_version_ranges()]

        plat_feat = []

        if platforms is not None:
            plat_feat.extend(platforms)

        if features is not None:
            plat_feat.extend(features)

        for vr_str in vranges_str:
            output.write(f'%If ({vr_str})\n', indent=False)

        if len(plat_feat) != 0:
            tags = ' || '.join(plat_feat)
            output.write(f'%If ({tags})\n', indent=False)

        output.write(
f'''%ModuleCode
#include <{sip_file.name}>
%End
''')

        if len(plat_feat) != 0:
            output.write('%End\n', indent=False)

        for _ in vranges_str:
            output.write('%End\n', indent=False)

        output.blank()

    for api in sip_file.content:
        if api.status == '':
            adapt(api).generate_sip(sip_file, output)

    output.blank()

    output.write_code_directive('%ExportedHeaderCode',
            sip_file.exportedheadercode, indent=False)
    output.write_code_directive('%ModuleHeaderCode', sip_file.moduleheadercode,
            indent=False)
    output.write_code_directive('%ModuleCode', sip_file.modulecode,
            indent=False)
    output.write_code_directive('%PreInitialisationCode', sip_file.preinitcode,
            indent=False)
    output.write_code_directive('%InitialisationCode', sip_file.initcode,
            indent=False)
    output.write_code_directive('%PostInitialisationCode',
            sip_file.postinitcode, indent=False)
    output.write_code_directive('%ExportedTypeHintCode',
            sip_file.exportedtypehintcode, indent=False)
    output.write_code_directive('%TypeHintCode', sip_file.typehintcode,
            indent=False)


class _IndentSipFile(IndentFile):
    """ An indentation file with extra functionality for writing .sip files.
    """

    def write_code_directive(self, directive, code, indent=True):
        """ Write a code directive. """

        if code != '':
            self.write(directive + '\n', indent=False)
            self += 1
            self.write(code + '\n', indent=indent)
            self -= 1
            self.write('%End\n', indent=False)
            self.blank()
