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


from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QDockWidget, QMainWindow, QMenuBar, QMessageBox

from .tools import ToolLocation


class Shell:
    """ This class encapsulates a collection of tools. """

    # Map tool locations to Qt dock areas.
    _LOCATION_MAP = {
        ToolLocation.LEFT: Qt.DockWidgetArea.LeftDockWidgetArea,
        ToolLocation.RIGHT: Qt.DockWidgetArea.RightDockWidgetArea,
        ToolLocation.TOP: Qt.DockWidgetArea.TopDockWidgetArea,
        ToolLocation.BOTTOM: Qt.DockWidgetArea.BottomDockWidgetArea,
    }

    def __init__(self, *tool_factories):
        """ Initialise the shell. """

        self._project = None

        # Create the widget that implements the shell.
        self._shell_widget = _ShellWidget(self._handle_close_event)
        self._shell_widget.setObjectName('metasip.shell')

        # Create the tools.
        self._tools = []
        menus = {}

        for tool_factory in tool_factories:
            tool = tool_factory(self)

            if tool.location is ToolLocation.CENTRE:
                self._shell_widget.setCentralWidget(tool.widget)
            else:
                self._shell_widget.addDockWidget(
                        self._LOCATION_MAP[tool.location],
                        QDockWidget(tool.title, tool.widget,
                                objectName=tool.name))

            # Add any actions to the menus.
            menu_name, actions = tool.actions
            if menu_name:
                menu_actions = menus.setdefault(menu_name, [])
                if len(menu_actions) != 0:
                    # This will turn into a separator.
                    menu_actions.append(None)

                menu_actions.extend(actions)

            self._tools.append(tool)

        # Create the menu bar.
        menu_bar = QMenuBar()

        for menu_name, actions in menus.items():
            menu = menu_bar.addMenu(menu_name)

            for action in actions:
                if action is None:
                    menu.addSeperator()
                else:
                    menu.addAction(action)

        self._shell_widget.setMenuBar(menu_bar)

        # Restore the state now the GUI has been built.
        settings = QSettings()

        for tool in self._tools:
            tool.restore_state(settings)

        setting = settings.value('state')
        if setting is not None:
            self._shell_widget.restoreState(setting)

        setting = settings.value('geometry')
        if setting is not None:
            self._shell_widget.restoreGeometry(setting)

    @property
    def dirty(self):
        """ Get the project's dirty state. """

        return self._project.dirty

    @dirty.setter
    def dirty(self, state):
        """ Set the dirty state. """

        # We do this here in case the project name has changed.
        self._shell_widget.setWindowTitle(self._project.name + '[*]')

        self._project.dirty = state
        self._shell_widget.setWindowModified(state)

    @property
    def project(self):
        """ Get the current project. """

        return self._project

    @project.setter
    def project(self, project):
        """ Set the current project. """

        self._project = project

        for tool in self._tools:
            tool.project = project

        self.dirty = False

    def save_project(self):
        """ Return True if any current project was saved. """

        # Ask the user unless the project hasn't been modified.
        if not self._project.dirty:
            return True

        button = QMessageBox.question(self._shell_widget, "Quit",
                "The project has been modified. Do you want to save or discard the changes?",
                QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Save)

        if button is QMessageBox.StandardButton.Cancel:
            return False

        if button is QMessageBox.StandardButton.Save:
            save_unsuccessful = False

            for tool in self._tools:
                if not tool.save_data():
                    save_unsuccessful = True

            if save_unsuccessful:
                return False

        return True

    def show(self):
        """ Make the shell visible. """

        self._shell_widget.show()

    def _handle_close_event(self):
        """ Handle a close event and return True if the event should be
        accepted.
        """

        if self.save_project():
            # Save the settings.
            settings = QSettings()
            settings.setValue('geometry', self._shell_widget.saveGeometry())
            settings.setValue('state', self._shell_widget.saveState())

            for tool in self._tools:
                tool.save_state(settings)

            return True

        return False


class _ShellWidget(QMainWindow):
    """ The widget that implements the shell. """

    def __init__(self, close_event_handler):
        """ Initialise the widget. """

        super().__init__()

        self._close_event_handler = close_event_handler

    def closeEvent(self, event):
        """ Reimplemented to save the state of the GUI. """

        if self._close_event_handler():
            event.accept()
        else:
            event.ignore()
