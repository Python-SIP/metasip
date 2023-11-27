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


from PyQt6.QtWidgets import QSplitter

from .control_widget import ControlWidget
from .sources_widget import SourcesWidget


class ScannerWidget(QSplitter):
    """ This class is a widget that implements a scanner's GUI. """

    def __init__(self, tool):
        """ Initialise the widget. """

        super().__init__()

        self._tool = tool

        self._sources = SourcesWidget()
        self.addWidget(self._sources)

        self._control = ControlWidget()
        self.addWidget(self._control)
