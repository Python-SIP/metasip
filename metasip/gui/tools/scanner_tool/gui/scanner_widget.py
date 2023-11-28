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

        self._sources = SourcesWidget(tool)
        self.addWidget(self._sources)

        self._control = ControlWidget(tool)
        self.addWidget(self._control)

    def rename_version(self, old_name, new_name):
        """ Rename a version. """

        self._control.rename_version(old_name, new_name)

    def restore_state(self, settings):
        """ Restore the widget's state. """

        settings.beginGroup('control')
        self._control.restore_state(settings)
        settings.endGroup()

        settings.beginGroup('sources')
        self._sources.restore_state(settings)
        settings.endGroup()

        state = settings.value('splitter')
        if state is not None:
            self.restoreState(state)

    def save_state(self, settings):
        """ Save the widget's state. """

        settings.setValue('splitter', self.saveState())

        settings.beginGroup('sources')
        self._sources.save_state(settings)
        settings.endGroup()

        settings.beginGroup('control')
        self._control.save_state(settings)
        settings.endGroup()

    def set_project(self):
        """ Set the current project. """

        self._sources.set_project()
        self._control.set_project()

    def update_versions(self):
        """ Update the versions. """

        self._control.update_versions()
