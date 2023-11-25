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


from enum import auto, Enum

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QDockWidget, QMainWindow, QMenuBar, QMessageBox

from .shell_tool import ShellTool, ShellToolLocation


class EventType(Enum):
    """ The different project-related event types. """

    # A feature has been added or deleted.  There is no event argument.
    FEATURE_ADD_DELETE = auto()

    # A message has been logged.  The message is the event argument.
    LOG_MESSAGE = auto()

    # A module has been added or deleted.  There is no event argument.
    MODULE_ADD_DELETE = auto()

    # A platform has been added or deleted.  There is no event argument.
    PLATFORM_ADD_DELETE = auto()

    # A new project has been loaded.  There is no event argument.
    PROJECT_NEW = auto()

    # A version has been added or deleted.  There is no event argument.
    VERSION_ADD_DELETE = auto()


class Shell:
    """ This class encapsulates a collection of tools. """

    # Map tool locations to Qt dock areas.
    _LOCATION_MAP = {
        ShellToolLocation.LEFT: Qt.DockWidgetArea.LeftDockWidgetArea,
        ShellToolLocation.RIGHT: Qt.DockWidgetArea.RightDockWidgetArea,
        ShellToolLocation.TOP: Qt.DockWidgetArea.TopDockWidgetArea,
        ShellToolLocation.BOTTOM: Qt.DockWidgetArea.BottomDockWidgetArea,
    }

    def __init__(self, *tool_factories):
        """ Initialise the shell. """

        self._project = None

        # Create the widget that implements the shell.
        self.shell_widget = _ShellWidget(self._handle_close_event)
        self.shell_widget.setObjectName('metasip.shell')

        # Create the tools.
        self._tools = []
        menus = {}
        view_actions = []

        for tool_factory in tool_factories:
            tool = tool_factory(self)

            if isinstance(tool, ShellTool):
                if tool.location is ShellToolLocation.CENTRE:
                    self.shell_widget.setCentralWidget(tool.widget)
                else:
                    dock_widget = QDockWidget(tool.title, tool.widget,
                            objectName=tool.name)
                    self.shell_widget.addDockWidget(
                            self._LOCATION_MAP[tool.location], dock_widget)
                    view_actions.append(dock_widget.toggleViewAction())

            # Add any actions to the menus.
            menu_name, actions = tool.actions
            if menu_name:
                menu_actions = menus.setdefault(menu_name, [])
                if len(menu_actions) != 0:
                    # This will turn into a separator.
                    menu_actions.append(None)

                menu_actions.extend(actions)

            self._tools.append(tool)

        # Add any view actions to the View menu.
        if len(view_actions) != 0:
            all_view_actions = menus.setdefault("View", [])
            if len(all_view_actions) != 0:
                all_view_actions.append(None)

            all_view_actions.extend(view_actions)

        # Create the menu bar.
        menu_bar = QMenuBar()

        def add_menu(menu_name, actions):
            menu = menu_bar.addMenu(menu_name)

            for action in actions:
                if action is None:
                    menu.addSeparator()
                else:
                    menu.addAction(action)

        # Make sure any well known menus are created in the expected order.
        for menu_name in ("File", "Edit", "View", "Tools"):
            actions = menus.pop(menu_name, None)
            if actions is not None:
                add_menu(menu_name, actions)

        # Now do any remaining menus.
        for menu_name, actions in menus.items():
            add_menu(menu_name, actions)

        self.shell_widget.setMenuBar(menu_bar)

        # Restore the state now the GUI has been built.
        settings = QSettings()

        for tool in self._tools:
            tool.restore_state(settings)

        setting = settings.value('state')
        if setting is not None:
            self.shell_widget.restoreState(setting)

        setting = settings.value('geometry')
        if setting is not None:
            self.shell_widget.restoreGeometry(setting)

    @property
    def dirty(self):
        """ Get the project's dirty state. """

        return self._project.dirty

    @dirty.setter
    def dirty(self, state):
        """ Set the dirty state. """

        # We do this here in case the project name has changed.
        self.shell_widget.setWindowTitle(self._project.name + '[*]')

        self._project.dirty = state
        self.shell_widget.setWindowModified(state)

    def handle_project_dialog(self, title, dialog_factory, event_type=None):
        """ Handle a dialog that will update some aspect of a project. """

        dialog = dialog_factory(self._project, title, self.shell_widget)

        if dialog.update():
            self.dirty = True

            if event_type is not None:
                self.notify(event_type)

    def log(self, message):
        """ Log a message. """

        self.notify(EventType.LOG_MESSAGE, message)

    def notify(self, event_type, event_arg=None):
        """ Notify all tools about a project-specific event. """

        for tool in self._tools:
            tool.event(event_type, event_arg)

    @property
    def project(self):
        """ Get the current project. """

        return self._project

    @project.setter
    def project(self, project):
        """ Set the current project. """

        self._project = project
        self.notify(EventType.PROJECT_NEW)
        self.dirty = False

    def save_project(self):
        """ Return True if any current project was saved. """

        # Ask the user unless the project hasn't been modified.
        if not self._project.dirty:
            return True

        button = QMessageBox.question(self.shell_widget, "Quit",
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

        self.shell_widget.show()

    def _handle_close_event(self):
        """ Handle a close event and return True if the event should be
        accepted.
        """

        if self.save_project():
            # Save the settings.
            settings = QSettings()
            settings.setValue('geometry', self.shell_widget.saveGeometry())
            settings.setValue('state', self.shell_widget.saveState())

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
