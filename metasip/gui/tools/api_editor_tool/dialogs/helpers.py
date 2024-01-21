# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


class BaseType:
    """ This class implements helpers for the BaseType annotation. """

    BASE_TYPES = ('Enum', 'Flag', 'IntEnum', 'UIntEnum', 'IntFlag')

    def __init__(self, combo):
        """ Initialise the combo-box. """

        combo.addItems(self.BASE_TYPES)

        self._combo = combo

    def setAnnotation(self, anno):
        """ Set the current annotation. """

        for index, base_type in enumerate(self.BASE_TYPES):
            if base_type == anno:
                self._combo.setCurrentIndex(index)
                break;

    def annotation(self, annos_list):
        """ Get the current annotation. """

        base_type = str(self._combo.currentText())

        if base_type != 'Enum':
            annos_list.append('BaseType=' + base_type)


class Encoding:
    """ This class implements helpers for the Encoding annotation. """

    ENCODINGS = ('Default', 'None', 'ASCII', 'Latin-1', 'UTF-8')

    def __init__(self, combo):
        """ Initialise the combo-box. """

        combo.addItems(self.ENCODINGS)

        self._combo = combo

    def setAnnotation(self, anno):
        """ Set the current annotation. """

        for index, encoding in enumerate(self.ENCODINGS):
            if encoding == anno:
                self._combo.setCurrentIndex(index)
                break

    def annotation(self, annos_list):
        """ Get the current annotation. """

        encoding = str(self._combo.currentText())

        if encoding != 'Default':
            annos_list.append(f'Encoding="{encoding}"')


def split_annos(anno_s):
    """ Split a number of annotations represented as a string into a sequence
    of 2-tuple name/value pairs.
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
                annos.append((name.strip(), value))
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
                    name = anno_s[part_start:i].strip()
                    value = None
                elif expecting == VALUE:
                    value = anno_s[part_start:i].strip()

                annos.append((name, value))

                expecting = NAME
                part_start = i + 1

    return annos
