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


""" This module handles annotations. """


def split_annos(anno_s):
    """ Split a number of annotations represented as a string into a sequence
    if name/value pairs.  The string is assumed to be well formed (ie. no
    superfluous spaces).
    """

    # Handle the trvial case.
    if anno_s == '':
        return []

    # This makes parsing easier.
    anno_s += ','

    NAME, VALUE, END_QUOTE, COMMA = range(4)

    annos = []
    expecting = NAME
    part_start = 0
    name = None

    for i, ch in enumerate(anno_s):
        if expecting == END_QUOTE:
            if ch == '"':
                value = anno_s[part_start:i]
                annos.append((name, value))
                expecting = COMMA
        else:
            if ch == '=':
                name = anno_s[part_start:i]
                expecting = VALUE
                part_start = i + 1
            elif ch == '"':
                expecting = END_QUOTE
                part_start = i + 1
            elif ch == ',':
                if expecting == NAME:
                    name = anno_s[part_start:i]
                    value = None
                elif expecting == VALUE:
                    value = anno_s[part_start:i]

                annos.append((name, value))

                expecting = NAME
                part_start = i + 1

    return annos
