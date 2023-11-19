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


from ..abstract_tool import AbstractTool, ToolLocation

from .api_editor import ApiEditor


class ApiEditorTool(AbstractTool):
    """ This class implements the API editor tool. """

    def __init__(self, shell):
        """ Initialise the tool. """

        super().__init__(shell)

        self._api_editor = ApiEditor(self)

    @property
    def location(self):
        """ Get the location of the tool in the shell. """

        return ToolLocation.CENTRE

    @property
    def project(self):
        """ Get the current project. """

        return AbstractTool.project.fget(self)

    @project.setter
    def project(self, project):
        """ Set the current project. """

        AbstractTool.project.fset(self, project)

        self._api_editor.set_project(project)

    @property
    def title(self):
        """ Get the tool's title. """

        return "API Editor"

    @property
    def widget(self):
        """ Get the tool's widget. """

        return self._api_editor
