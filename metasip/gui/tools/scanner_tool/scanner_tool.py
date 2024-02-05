# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>



from ...shell import EventType
from ...shell_tool import ShellTool, ShellToolLocation

from .gui import ScannerGui


class ScannerTool(ShellTool):
    """ This class implements a tool for handling the scanning of a project's
    header directories.
    """

    def __init__(self, shell):
        """ Initialise the tool. """

        super().__init__(shell)

        self._gui = ScannerGui(self)

    def event(self, event_type, event_arg):
        """ Reimplemented to handle project-specific events. """

        if event_type in (EventType.MODULE_ADD, EventType.MODULE_DELETE):
            self._gui.control_widget.module_add_delete()
        elif event_type is EventType.MODULE_RENAME:
            self._gui.control_widget.module_rename(event_arg)
        elif event_type is EventType.PROJECT_NEW:
            self._set_project()
        elif event_type in (EventType.VERSION_ADD, EventType.VERSION_DELETE):
            self._gui.control_widget.version_add_delete()
        elif event_type is EventType.VERSION_RENAME:
            self._gui.control_widget.version_rename(*event_arg)

    def header_directory_added(self, header_directory, working_version):
        """ A header directory has been added. """

        self._gui.sources_widget.header_directory_added(header_directory,
                working_version)

    def header_directory_status(self, header_directory):
        """ The status of a header directory has changed. """

        self._gui.sources_widget.header_directory_status(header_directory)

    def header_directory_removed(self, header_directory):
        """ A header directory has been removed. """

        self._gui.sources_widget.header_directory_removed(header_directory)

    def header_file_added(self, header_file, header_directory, working_version):
        """ A header file has been added. """

        self._gui.sources_widget.header_file_added(header_file,
                header_directory, working_version)

    def header_file_status(self, header_file):
        """ The status of a header file has changed. """

        self._gui.sources_widget.header_file_status(header_file)

    def header_file_removed(self, header_file):
        """ A header file has been removed. """

        self._gui.sources_widget.header_directory_removed(header_file)

    @property
    def location(self):
        """ Get the location of the tool in the shell. """

        return ShellToolLocation.RIGHT

    @property
    def name(self):
        """ Get the tool's name. """

        return 'metasip.tool.scanner'

    def restore_state(self, settings):
        """ Restore the tool's state from the settings. """

        self._gui.restore_state(settings)

    def save_state(self, settings):
        """ Save the tool's state in the settings. """

        self._gui.save_state(settings)

    def set_header_file(self, header_file, header_directory, showing_ignored):
        """ Set the current header file. """

        self._gui.control_widget.set_header_file(header_file, header_directory,
                showing_ignored)

    def set_header_files_visibility(self, header_directory, showing_ignored):
        """ Show or hide all the ignored files in a header directory. """

        self._gui.sources_widget.set_header_files_visibility(header_directory,
                showing_ignored)

    def set_working_version(self, working_version):
        """ Set the current working version. """

        self._gui.sources_widget.set_working_version(working_version)
        self._gui.control_widget.set_working_version(working_version)

    @property
    def title(self):
        """ Get the tool's title. """

        return "Scanner"

    @property
    def widget(self):
        """ Get the tool's widget. """

        return self._gui

    def _set_project(self):
        """ Set the current project. """

        self._gui.sources_widget.set_project()
        self._gui.control_widget.set_project()

        project = self.shell.project

        # Default to the latest version if any.
        working_version = project.versions[-1] if len(project.versions) != 0 else None
        self.set_working_version(working_version)
