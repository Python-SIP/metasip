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


from ..dip.model import implements
from ..dip.shell import BaseManagedModelTool, IManagedModelTool
from ..dip.ui import IDisplay

from ..interfaces.project import IProject


@implements(IManagedModelTool, IDisplay)
class ProjectEditorTool(BaseManagedModelTool):
    """ The ProjectEditorTool implements the tool for editing a project. """

    # The tool's identifier.
    id = 'metasip.tools.project_editor'

    # The tool's name used in model manager dialogs and wizards.
    name = "MetaSIP project editor"

    def create_views(self, model):
        """ Create the views for editing a model. """

        from .api_editor import ApiEditor

        return [ApiEditor(model)]

    def handles(self, model):
        """ Check that the tool can handle a model. """

        return isinstance(model, IProject)
