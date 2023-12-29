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


def code_directive(directive, code, output, indent=True):
    """ Write a code directive to a .sip file. """

    if code != '':
        output.write(directive + '\n', indent=False)
        output += 1
        output.write(code + '\n', indent=indent)
        output -= 1
        output.write('%End\n', indent=False)
        output.blank()
