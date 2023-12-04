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


class ScannerGui(QSplitter):
    """ This class is a widget that implements a scanner's GUI. """

    def __init__(self, tool):
        """ Initialise the widget. """

        super().__init__()

        self.sources_widget = SourcesWidget(tool)
        self.addWidget(self.sources_widget)

        self.control_widget = ControlWidget(tool)
        self.addWidget(self.control_widget)

    def restore_state(self, settings):
        """ Restore the widget's state. """

        settings.beginGroup('control')
        self.control_widget.restore_state(settings)
        settings.endGroup()

        settings.beginGroup('sources')
        self.sources_widget.restore_state(settings)
        settings.endGroup()

        state = settings.value('splitter')
        if state is not None:
            self.restoreState(state)

    def save_state(self, settings):
        """ Save the widget's state. """

        settings.setValue('splitter', self.saveState())

        settings.beginGroup('sources')
        self.sources_widget.save_state(settings)
        settings.endGroup()

        settings.beginGroup('control')
        self.control_widget.save_state(settings)
        settings.endGroup()
