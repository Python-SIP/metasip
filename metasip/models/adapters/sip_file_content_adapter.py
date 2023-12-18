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


from .base_adapter import BaseAdapter


class SipFileContentAdapter(BaseAdapter):
    """ This is the base class for all adapters for APIs specified in a .sip
    file.
    """

    def generate_sip(self, output, project):
        """ Generates the .sip file representation. """

        # This default implementation just writes the string representation.
        # TODO: write_line() writes the indent, the line then a '\n'.
        # TODO: handle any versioning in a reusable way.
        f.write_line(self.as_str(project))

    @classmethod
    def expand_type(cls, type, name=None, project=None):
        """ Return the full type with an optional name. """

        # Handle the trivial case.
        if type == '':
            return ''

        if project is not None:
            const = 'const '
            if type.startswith(const):
                type = type[len(const):]
            else:
                const = ''

            type = const + cls.ignore_namespaces(type, project)

        # SIP can't handle every C++ fundamental type.
        # TODO: add the SIP support.
        type = type.replace('long int', 'long')

        # Append any name.
        s = type

        if name:
            if type[-1] not in '&*':
                s += ' '

            s += name

        return s

    @classmethod
    def ignore_namespaces(cls, type, project):
        """ Return a type with any namespaces to be ignored removed. """

        for ignored_namespace in project.ignorednamespaces:
            namespace_prefix = ignored_namespace + '::'

            if type.startswith(namespace_prefix):
                type = type[len(namespace_prefix):]
                break

        # Handle any template arguments.
        t_start = type.find('<')
        t_end = type.rfind('>')

        if t_start > 0 and t_end > t_start:
            t_args = []

            # Note that this doesn't handle nested template arguments properly.
            for t_arg in type[t_start + 1:t_end].split(','):
                t_args.append(cls.ignore_namespaces(t_arg.strip(), project))

            type = type[:t_start + 1] + ', '.join(t_args) + type[t_end:]

        return type
