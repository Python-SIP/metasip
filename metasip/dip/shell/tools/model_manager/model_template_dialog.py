# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of dip.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from ....model import Any, Instance, Str
from ....ui import Dialog, Label, OptionList, VBox

from .model_manager_tool import ModelManagerTool


class ModelTemplateDialog(Dialog):
    """ ModelTemplateDialog is an internal class that implements the dialog that
    asks the user to select a model template.
    """

    # The model template.
    model_template = Any()

    # The managed model manager using the dialog.
    model_manager = Instance(ModelManagerTool)

    # The prompt to use in the dialog.
    _prompt = Str()

    def __init__(self):
        """ Initialise the dialog factory. """

        manager = self.model_manager

        self._prompt = manager.choose_new_model_prompt

        model_templates, labels = manager._resources.model_templates_for_new()

        content = VBox(Label('_prompt'),
                OptionList('model_template', allow_none=False, labels=labels,
                        options=model_templates, sorted=True))

        super().__init__(content, title=manager.user_new_title)

    def execute(self):
        """ Create and execute the dialog.  Return True if the user accepted.
        """

        dialog = self(self, parent=self.model_manager.shell)

        return dialog.execute()
