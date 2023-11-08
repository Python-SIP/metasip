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


from ...dip.model import implements, Model, observe
from ...dip.publish import ISubscriber
from ...dip.shell import IDirty, ITool
from ...dip.ui import (Action, IAction, ActionCollection, CheckBox, ComboBox,
        Dialog, IDialog, DialogController, Form, LineEditor, MessageArea, VBox)

from ...interfaces.project import IProject
from ...utils.project import validate_identifier

# FIXME: We should not need to know about the actual IProject implementation.
from ...Project import Module


class ModuleController(DialogController):
    """ A controller for a dialog containing an editor for a module. """

    def validate_view(self):
        """ Validate the view. """

        module = self.view.module.value

        message = validate_identifier(module, "module")
        if message != "":
            return message

        for m in self.model.project.modules:
            if m.name == module:
                return "A module has already been defined with the same name."

        if module in self.model.project.externalmodules:
            return "An external module has already been defined with the same name."

        return ""


@implements(ITool, ISubscriber)
class ModulesTool(Model):
    """ The ModulesTool implements a tool for handling a project's set of
    modules.
    """

    # The delete module dialog.
    dialog_delete = Dialog(ComboBox('module', options='modules'),
            title="Delete Module")

    # The new module dialog.
    dialog_new = Dialog(
            VBox(Form('module'),
                    CheckBox('external',
                            label="The module is defined in another project"),
                    MessageArea()),
            title="New Module", controller_factory=ModuleController)

    # The rename module dialog.
    dialog_rename = Dialog(
            ComboBox('old_name', label="Module", options='modules'),
            LineEditor('module', label="New name"), MessageArea(),
            title="Rename Module", controller_factory=ModuleController)

    # The tool's identifier.
    id = 'metasip.tools.modules'

    # The delete module action.
    module_delete = Action(enabled=False, text="Delete Module...")

    # The new module action.
    module_new = Action(text="New Module...")

    # The rename module action.
    module_rename = Action(enabled=False, text="Rename Module...")

    # The collection of the tool's actions.
    modules_actions = ActionCollection(text="Modules",
            actions=['module_new', 'module_rename', 'module_delete'],
            within='dip.ui.collections.edit')

    # The type of models we subscribe to.
    subscription_type = IProject

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        project = change.new.model

        are_modules = (len(project.modules) + len(project.externalmodules) != 0)

        IAction(self.module_rename).enabled = are_modules
        IAction(self.module_delete).enabled = are_modules

    @module_delete.triggered
    def module_delete(self):
        """ Invoked when the delete module action is triggered. """

        project = self.subscription.model
        all_modules = self._all_modules(project)
        model = dict(module=all_modules[0], modules=all_modules)

        dlg = self.dialog_delete(model)

        if IDialog(dlg).execute():
            module = model['module']

            # Delete from the project's list.
            for m in project.modules:
                if m.name == module:
                    project.modules.remove(m)
                    break
            else:
                project.externalmodules.remove(module)

            IDirty(project).dirty = True

            self._update_actions()

    @module_new.triggered
    def module_new(self):
        """ Invoked when the new module action is triggered. """

        project = self.subscription.model
        model = dict(project=project, module='', external=False)

        dlg = self.dialog_new(model)

        if IDialog(dlg).execute():
            module = model['module']
            external = model['external']

            if external:
                project.externalmodules.append(module)
            else:
                project.modules.append(Module(name=module))

            IDirty(project).dirty = True

            self._update_actions()

    @module_rename.triggered
    def module_rename(self):
        """ Invoked when the rename module action is triggered. """

        project = self.subscription.model
        all_modules = self._all_modules(project)
        model = dict(project=project, module='', old_name=all_modules[0],
                modules=all_modules)

        dlg = self.dialog_rename(model)

        if IDialog(dlg).execute():
            old_name = model['old_name']
            new_name = model['module']

            # Rename in the project's list.
            for m in project.modules:
                if m.name == old_name:
                    m.name = new_name
                    break
            else:
                project.externalmodules[project.externalmodules.index(old_name)] = new_name

            IDirty(project).dirty = True

    def _update_actions(self):
        """ Update the enabled state of the rename and delete actions. """

        are_modules = (len(self.subscription.model.modules) != 0)

        IAction(self.module_rename).enabled = are_modules
        IAction(self.module_delete).enabled = are_modules

    @staticmethod
    def _all_modules(project):
        """ Return the sorted list of all the modules of a project. """

        return sorted(
                [m.name for m in project.modules] + project.externalmodules)
