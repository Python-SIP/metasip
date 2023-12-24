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


from .adapt import adapt
from .base_adapter import BaseAdapter


class CodeContainerAdapter(BaseAdapter):
    """ This is the CodeContainer adapter. """

    def load(self, tag_code_map, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        for subelement in element:
            # All sub-classes happen to have literals.
            if subelement.tag == 'Literal':
                self.set_literal(subelement)
            else:
                model = tag_code_map[subelement.tag]()
                adapt(model).load(subelement, ui)
                self.model.content.append(model)
