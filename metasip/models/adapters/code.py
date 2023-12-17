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


from ..annos import Annos
from ..tagged import Tagged
from ..workflow import Workflow

from .adapt import adapt
from .base_adapter import BaseAdapter


class CodeAdapter(BaseAdapter):
    """ This is the Code adapter. """

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        # Note that the 'container' attribute will be set by the CodeContainer
        # adapter.
        adapt(self.model, Annos).load(element, ui)
        adapt(self.model, Tagged).load(element, ui)
        adapt(self.model, Workflow).load(element, ui)