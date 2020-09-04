# Copyright (c) 2020 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.io import IFilterHints
from dip.model import implements, Model
from dip.publish import ISubscriber
from dip.shell import ITool
from dip.ui import (Action, IAction, Dialog, IDialog, DialogController,
        StorageLocationEditor)

from ...interfaces.project import IProject


class _DialogController(DialogController):
    """ An internal class that implements the controller for the schema
    validator dialog.
    """

    def validate(self):
        """ Reimplemented to change the configuration of the dialog. """

        # Do the normal validation.
        super().validate()


@implements(ITool, ISubscriber)
class ImportProjectTool(Model):
    """ The ImportProjectTool implements a tool importing another project. """

    # The tool's dialog.
    dialog = Dialog(StorageLocationEditor('project_file', required=True),
            title="Import Project", controller_factory=_DialogController)

    # The tool's identifier.
    id = 'metasip.tools.import_project'

    # The action.
    import_action = Action(text="Import Project...",
            within='dip.ui.collections.tools')

    # The type of models we subscribe to.
    subscription_type = IProject

    @import_action.triggered
    def import_action(self):
        """ Invoked when the import action is triggered. """

        model = dict(project_file='')

        view = self.dialog(model)
        view.project_file.filter = IFilterHints(self.subscription.model).filter

        if IDialog(view).execute():
            print("Importing", model['project_file'])
