# Copyright (c) 2018 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.model import implements, Model, observe, Str
from dip.publish import ISubscriber
from dip.shell import ITool
from dip.ui import (Action, IAction, ComboBox, Dialog, IDialog,
        DialogController, IEditor, Form, Label, MessageArea, VBox)

from ...interfaces.project import IProject


class _DialogController(DialogController):
    """ An internal class that implements the controller for the auto-fill
    module dialog.
    """

    def validate_view(self):
        """ Validate the data in the view. """

        # Check the source and destination modules are different.
        source_module = IEditor(self.source_module_editor).value
        destination_module = IEditor(self.destination_module_editor).value

        if source_module == destination_module:
            invalid_reason = "The source and destination modules must be different."
        else:
            invalid_reason = ''

        return invalid_reason


@implements(ISubscriber, ITool)
class ModuleAutofillTool(Model):
    """ The ModuleAutofillTool class implements a tool for auto-filling
    unchecked items in one module from checked items in another module.
    """

    # The tool's dialog.
    dialog = Dialog(
            VBox(Label('prompt'),
                    Form(ComboBox('source_module', options='modules'),
                            ComboBox('destination_module', options='modules')),
                    MessageArea()),
            controller_factory=_DialogController)

    # The prompt to use in the dialog.
    dialog_prompt = Str(
            "Select the source and destination modules.  The annotations and\n"
            "handwritten code of unchecked callables in the destination\n"
            "module will be updated from checked callables with the same\n"
            "C/C++ signature in the source module.")

    # The tool's identifier.
    id = 'metasip.tools.module_autofill'

    # The action.
    autofill_action = Action(text="Auto-fill Module...", enabled=False,
            within='dip.ui.collections.tools')

    # The type of models we subscribe to.
    subscription_type = IProject

    @autofill_action.triggered
    def autofill_action(self):
        """ Invoked when the auto-fill action is triggered. """

        title = IAction(self.autofill_action).plain_text
        project = self.subscription.model
        modules = project.modules

        model = dict(prompt=self.dialog_prompt, source_module=modules[0],
                destination_module=modules[0], modules=modules)

        view = self.dialog(model, title=title)

        if IDialog(view).execute():
            from .autofill_module import autofill_module

            autofill_module(project, model['source_module'],
                    model['destination_module'])

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        event = change.new.event
        project = change.new.model

        if event == 'dip.events.opened':
            IAction(self.autofill_action).enabled = (len(project.modules) > 1)
            observe('modules', project, self.__on_modules_changed)
        elif event == 'dip.events.closed':
            observe('modules', project, self.__on_modules_changed, remove=True)
            IAction(self.autofill_action).enabled = False

    def __on_modules_changed(self, change):
        """ Invoked when the list of modules in the current project changes.
        """

        IAction(self.autofill_action).enabled = (len(change.model.modules) > 1)
