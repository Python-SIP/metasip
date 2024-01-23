# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from enum import auto, Enum

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (QDockWidget, QMainWindow, QMenuBar, QMessageBox,
        QWhatsThis)

from .._version import version

from .shell_tool import ShellTool, ShellToolLocation


class EventType(Enum):
    """ The different project-related event types.  These are only used to
    update the different parts of the GUI and so there are many similar changes
    that don't have an event because there is no consequent impact on the GUI.
    """

    # The status of an API model has changed.  The event argument is the API.
    API_STATUS = auto()

    # The versions of an API model has changed.  The event argument is the API.
    API_VERSIONS = auto()

    # An API model has been added to a container model.  The event argument is
    # a 2-tuple of the container and API.
    CONTAINER_API_ADD = auto()

    # An API model has been deleted from a container model.  The event argument
    # is a 2-tuple of the container and API.
    CONTAINER_API_DELETE = auto()

    # A feature has been added.  The event argument is the name of the feature.
    FEATURE_ADD = auto()

    # A feature has been deleted.  The event argument is the name of the
    # feature.
    FEATURE_DELETE = auto()

    # A feature has been renamed.  The event argument is a 2-tuple of the old
    # and new names.
    FEATURE_RENAME = auto()

    # A message has been logged.  The message is the event argument.
    LOG_MESSAGE = auto()

    # A module model has been added.  The event argument is the module.
    MODULE_ADD = auto()

    # A module model has been deleted.  The event argument is the module.
    MODULE_DELETE = auto()

    # A module model has been renamed.  The event argument is the module.
    MODULE_RENAME = auto()

    # A platform has been added.  The event argument is the name of the
    # platform.
    PLATFORM_ADD = auto()

    # A platform has been deleted.  The event argument is the name of the
    # platform.
    PLATFORM_DELETE = auto()

    # A platform has been renamed.  The event argument is a 2-tuple of the old
    # and new names.
    PLATFORM_RENAME = auto()

    # A new project has been loaded.  There is no event argument.
    PROJECT_NEW = auto()

    # A project has been renamed.  There is no event argument.
    PROJECT_RENAME = auto()

    # The project's root module has been renamed.  There is no event argument.
    PROJECT_ROOT_MODULE_RENAME = auto()

    # A version has been added.  The event argument is the name of the version.
    VERSION_ADD = auto()

    # A version has been deleted.  The event argument is the name of the
    # version.
    VERSION_DELETE = auto()

    # A version has been renamed.  The event argument is a 2-tuple of the old
    # and new names.
    VERSION_RENAME = auto()


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
        self.widget = _ShellWidget(self._handle_close_event)

        # Create the tools.
        self._tools = []
        menus = {}
        view_actions = []

        for tool_factory in tool_factories:
            tool = tool_factory(self)

            if isinstance(tool, ShellTool):
                if tool.location is ShellToolLocation.CENTRE:
                    self.widget.setCentralWidget(tool.widget)
                else:
                    dock_widget = QDockWidget(tool.title, objectName=tool.name)
                    dock_widget.setWidget(tool.widget)
                    self.widget.addDockWidget(
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

        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction("About msip...", self._about)
        help_menu.addAction(QWhatsThis.createAction(help_menu))

        self.widget.setMenuBar(menu_bar)

        # Restore the state now the GUI has been built.
        settings = QSettings()

        for tool in self._tools:
            settings.beginGroup(tool.name)
            tool.restore_state(settings)
            settings.endGroup()

        settings.beginGroup('metasip.shell')

        setting = settings.value('state')
        if setting is not None:
            self.widget.restoreState(setting)

        setting = settings.value('geometry')
        if setting is not None:
            self.widget.restoreGeometry(setting)

        settings.endGroup()

    @property
    def dirty(self):
        """ Get the project's dirty state. """

        return self._project.dirty

    @dirty.setter
    def dirty(self, state):
        """ Set the dirty state. """

        # We do this here in case the project name has changed.
        self.widget.setWindowTitle(self._project.name + '[*]')

        self._project.dirty = state
        self.widget.setWindowModified(state)

    def handle_project_dialog(self, title, dialog_factory):
        """ Handle a dialog that will update some aspect of a project. """

        dialog = dialog_factory(self._project, title, self)

        if dialog.update():
            self.dirty = True

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
        self.dirty = project.dirty

    def save_project(self):
        """ Return True if any current project was saved. """

        # Ask the user unless the project hasn't been modified.
        if not self._project.dirty:
            return True

        button = QMessageBox.question(self.widget, "Quit",
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

        self.widget.show()

    def _about(self):
        """ Tell the user about the application. """

        QMessageBox.about(self.widget, "About msip",
f"""This is msip v{version}, part of MetaSIP.

msip is a tool for creating .sip files from C/C++ header files.
""")

    def _handle_close_event(self):
        """ Handle a close event and return True if the event should be
        accepted.
        """

        if self.save_project():
            # Save the settings.
            settings = QSettings()

            settings.beginGroup('metasip.shell')
            settings.setValue('geometry', self.widget.saveGeometry())
            settings.setValue('state', self.widget.saveState())
            settings.endGroup()

            for tool in self._tools:
                settings.beginGroup(tool.name)
                tool.save_state(settings)
                settings.endGroup()

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
