# Copyright (c) 2013 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.shell import IDirty

from ...interfaces.project import ICallable, ICodeContainer


def autofill_module(project, source, destination):
    """ Auto-fill unchecked items in the destination module from checked items
    in the source module.
    """

    source_callables = list(_module_callables(source, status=''))

    for dst in _module_callables(destination, status='unknown'):
        # See if there is a matching source callable.
        for src in source_callables:
            if dst.name != src.name or dst.rtype != src.rtype:
                continue
                
            if len(dst.args) != len(src.args):
                continue

            args_different = False
            for a in range(len(dst.args)):
                if dst.args[a].type != src.args[a].type:
                    args_different = True
                    break

            if args_different:
                continue

            # Fill the destination.
            dst.methcode = src.methcode
            dst.pyargs = src.pyargs
            dst.pytype = src.pytype

            dst.features = list(src.features)
            dst.platforms = list(src.platforms)

            dst.annos = src.annos

            for a in range(len(dst.args)):
                dst.args[a].annos = src.args[a].annos
                dst.args[a].pydefault = src.args[a].pydefault
                dst.args[a].pytype = src.args[a].pytype

            dst.status = ''

            IDirty(project).dirty = True

            break


def _module_callables(module, status):
    """ A generator for all the callables of a module with a particular status.
    """

    for sip_file in module.content:
        for code in _code_container_callables(sip_file, status):
            yield code


def _code_container_callables(container, status):
    """ A generator for all the callables of a code container with a particular
    status.
    """

    for code in container.content:
        if code.status != 'ignored':
            if isinstance(code, ICallable):
                if code.status == status:
                    yield code
            elif isinstance(code, ICodeContainer):
                for sub_code in _code_container_callables(code, status):
                    yield sub_code
