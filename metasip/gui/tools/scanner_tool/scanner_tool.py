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

        if event_type is EventType.MODULE_RENAME:
            self._gui.control_widget.module_rename(*event_arg)
        elif event_type is EventType.PROJECT_NEW:
            self._set_project()
        elif event_type is EventType.VERSION_ADD_DELETE:
            self._gui.control_widget.version_add_delete()
        elif event_type is EventType.VERSION_RENAME:
            self._gui.control_widget.version_rename(*event_arg)

    @property
    def location(self):
        """ Get the location of the tool in the shell. """

        return ShellToolLocation.RIGHT

    @property
    def name(self):
        """ Get the tool's name. """

        return 'metasip.tool.scanner'

    def new_header_directory(self, header_directory, working_version):
        """ A new header directory has been added. """

        self._gui.sources_widget.new_header_directory(header_directory,
                working_version)

    def restore_state(self, settings):
        """ Restore the tool's state from the settings. """

        self._gui.restore_state(settings)

    def save_state(self, settings):
        """ Save the tool's state in the settings. """

        self._gui.save_state(settings)

    def set_header_directories_state(self):
        """ Set the state of all header directories. """

        self._gui.sources_widget.set_header_directories_state()

    def set_header_file(self, header_file, header_directory, showing_ignored):
        """ Set the current header file. """

        self._gui.control_widget.set_header_file(header_file, header_directory,
                showing_ignored)

    def set_header_file_state(self, header_file):
        """ Set the state of a header file. """

        self._gui.sources_widget.set_header_file_state(header_file)

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
