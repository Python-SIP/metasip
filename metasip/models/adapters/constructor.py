# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..access import Access
from ..callable import Callable
from ..docstring import Docstring

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class ConstructorAdapter(BaseApiAdapter):
    """ This is the Constructor adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'explicit': AttributeType.BOOL,
    }

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        ctor = self.model
        other_ctor = other.model

        if type(ctor) is not type(other_ctor):
            return False

        if adapt(ctor, Callable) != adapt(other_ctor, Callable):
            return False

        if ctor.access != other_ctor.access:
            return False

        if ctor.explicit != other_ctor.explicit:
            return False

        return True

    def as_str(self):
        """ Return the standard string representation. """

        ctor = self.model

        s = adapt(ctor, Callable).as_str()

        if ctor.explicit:
            s = 'explicit ' + s

        return s

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        ctor = self.model

        nr_ends = self.version_start(output)

        output.write(self.as_str())
        output.write(';\n')

        adapt(ctor, Docstring).generate_sip_directives(output)
        adapt(ctor, Callable).generate_sip_directives(output)

        self.version_end(nr_ends, output)

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, Callable).load(element, project, ui)
        adapt(self.model, Docstring).load(element, project, ui)
        adapt(self.model, Access).load(element, project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        ctor = self.model

        output.write('<Constructor')
        adapt(ctor, Callable).save_attributes(output)
        adapt(ctor, Docstring).save_attributes(output)
        adapt(ctor, Access).save_attributes(output)
        self.save_bool('explicit', output)
        output.write('>\n')

        output += 1
        # The order is to match older versions.
        adapt(ctor, Docstring).save_subelements(output)
        adapt(ctor, Callable).save_subelements(output)
        adapt(ctor, Access).save_subelements(output)
        output -= 1

        output.write('</Constructor>\n')
