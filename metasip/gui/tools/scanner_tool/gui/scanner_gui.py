# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
