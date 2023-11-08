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


from ....io import IoManager, IStorageLocation, StorageError
from ....model import implements, Instance, Model, observe, Str, unadapted
from ....publish import Publication, IPublisher
from ....ui import Application, IDisplay, IView
from ....ui.actions import (CloseAction, NewAction, OpenAction, SaveAction,
        SaveAsAction)

from ... import (IDirty, IManagedModel, IManagedModelTool, IModelManagerTool,
        IQuitVeto)

from .resources_state import ResourcesState


@implements(IModelManagerTool, IDirty, IPublisher, IQuitVeto)
class ModelManagerTool(Model):
    """ The ModelManagerTool class is a :term:`tool` that handles the lifecycle
    of :term:`managed models<managed model>` in a :term:`shell`.
    """

    # The title of the wizard page to choose a model.
    choose_model_wizard_title = Str("Choose an item")

    # The text to use to prompt the user to choose a new model.
    # FIXME: The newlines are needed for OS/X (don't know about other
    # FIXME: platforms).  Should it be moved to the toolkit implementation?
    choose_new_model_prompt = Str("From the list below choose what sort of item you want to create.\n")

    # The text to use to prompt the user to choose a model to open.
    choose_open_model_prompt = Str("From the list below choose what sort of item you want to open.\n")

    # The text to use to prompt the user to choose a tool.
    choose_tool_prompt = Str("From the list below choose what tool you want to use.\n")

    # The title of the wizard page to choose a tool.
    choose_tool_wizard_title = Str("Choose a tool")

    # The Close action.
    close_action = CloseAction()

    # The tool's identifier.
    id = 'dip.shell.tools.model_manager'

    # The New action.
    new_action = NewAction()

    # The Open action.
    open_action = OpenAction()

    # The Save action.
    save_action = SaveAction()

    # The Save As action.
    save_as_action = SaveAsAction()

    # The text used as the question asking if the user really wants to close.
    user_close_question = Str("Do you still want to close?")

    # The text used as the title of the "Close" related views.
    user_close_title = Str()

    # The text used as the title of the "New" related views.
    user_new_title = Str()

    # The text used as the title of the "Open" related views.
    user_open_title = Str()

    # The text used as the title of the "Save" related views.
    user_save_title = Str()

    # The text used as the title of the "Save As" related views.
    user_save_as_title = Str()

    # The current managed model.
    _current_managed_model = Instance(IManagedModel)

    # The current managed model tool.
    _current_managed_model_tool = Instance(IManagedModelTool)

    # The current default location to use when opening a model.
    _default_location = Instance(IStorageLocation)

    # The state of the different resources and their interrelationships.
    _resources = Instance(ResourcesState)

    def __init__(self):
        """ Initialise the tool. """

        super().__init__()

        iomanager = IoManager().instance
        observe('codecs', iomanager, lambda c: self._update_resources())
        observe('storage_factories', iomanager,
                lambda c: self._update_resources())

    def veto_close_view(self, view, tool):
        """ This handles :meth:`~dip.shell.ICloseViewVeto.veto` on behalf of an
        implementation of the :class:`~dip.shell.IManagedModelTool` interface.

        :param view:
            is the view.
        :param tool:
            is the tool.
        :return:
            ``True`` if the close of the view is to be prevented.
        """

        model_to_remove = None

        # Find the model related to the view.
        for managed_model in tool.models:
            if view in managed_model.views:
                if managed_model.dirty:
                    if managed_model.invalid_reason != '':
                        answer = Application.question(self.user_close_title,
                                self._no_save_reason(managed_model),
                                detail=managed_model.invalid_reason,
                                parent=self.shell,
                                buttons=('cancel', 'discard'))

                        if answer == 'discard':
                            model_to_remove = managed_model
                    else:
                        answer = Application.question(self.user_close_title,
                                self._no_close_reason(managed_model),
                                parent=self.shell,
                                buttons=('save', 'cancel', 'discard'))

                        if answer == 'save':
                            # Do a Save or Save As.
                            if managed_model.location is None:
                                self._save_managed_model_as(managed_model)
                            else:
                                self._save_managed_model(managed_model)

                            # If the model is no longer dirty then it was
                            # written successfully.
                            if not managed_model.dirty:
                                model_to_remove = managed_model
                        elif answer == 'discard':
                            model_to_remove = managed_model
                else:
                    model_to_remove = managed_model

                break

        if model_to_remove is None:
            return True

        tool.models.remove(managed_model)
        self._publish_close(managed_model)

        return False

    def open_model(self, location, tool):
        """ This handles :meth:`~dip.shell.IOpenModel.open_model` on behalf of
        an implementation of the :class:`~dip.shell.IManagedModelTool`
        interface.

        :param location:
            is the storage location.
        :param tool:
            is the tool.
        """

        # There should be at least one codec and they all will have the same
        # format.
        format = location.storage.codecs[0].format

        managed_models = []
        abandoned = False

        for model_template in self._resources.model_templates():
            if not tool.handles(model_template):
                continue

            managed_model = self._resources.managed_model_from_template(
                    model_template)
            if managed_model.native_format != format:
                continue

            managed_model = self._read_managed_model(managed_model, location)
            if managed_model is None:
                abandoned = True
            else:
                managed_models.append(managed_model)

        nr_models = len(managed_models)

        if nr_models == 1:
            managed_model = managed_models[0]
            self._publish_open(managed_model)
            tool.models.append(managed_model)
        elif nr_models > 1:
            # Note that this is really a badly configured application.
            Application.warning(self.user_open_title,
                    "There are multiple types of item that can be read from "
                    "{0}".format(str(location)))
        elif not abandoned:
            # Only show a warning if there user hasn't already been involved.
            Application.warning(self.user_open_title,
                    "There is no type of item that can be read from "
                    "{0}".format(str(location)))

    @IQuitVeto.reasons.getter
    def reasons(self):
        """ Invoked to get the reasons why the application should not quit. """

        reasons = []

        for managed_model_tool in self._managed_model_tools():
            for managed_model in managed_model_tool.models:
                if managed_model.dirty:
                    reasons.append(self._no_close_reason(managed_model))

        return reasons

    @user_close_title.default
    def user_close_title(self):
        """ Invoked to return the default user close title. """

        return self.close_action.plain_text

    @user_new_title.default
    def user_new_title(self):
        """ Invoked to return the default user new title. """

        return self.new_action.plain_text

    @user_open_title.default
    def user_open_title(self):
        """ Invoked to return the default user open title. """

        return self.open_action.plain_text

    @user_save_title.default
    def user_save_title(self):
        """ Invoked to return the default user save title. """

        return self.save_action.plain_text

    @user_save_as_title.default
    def user_save_as_title(self):
        """ Invoked to return the default user save as title. """

        return self.save_as_action.plain_text

    @observe('model_factories')
    def __model_factories_changed(self, change):
        """ Invoked when the list of model factories changes. """

        self._update_resources()

        if self.shell is not None:
            self._auto_new(change.new)

    def __shell_ready(self, change):
        """ Invoked when the shell is ready to be made visible. """

        self._auto_new()

    def _auto_new(self, model_factories=None):
        """ Add new models to any tool whose model policy is 'one' but don't
        yet have a model.  Also manage the visibility of the Close action.
        """

        if model_factories is None:
            model_factories = self.model_factories

        close_visible = False

        # Get the list of candidate tools.
        managed_model_tools = []
        for managed_model_tool in self._managed_model_tools():
            if managed_model_tool.model_policy == 'one':
                if len(managed_model_tool.models) == 0:
                    managed_model_tools.append(managed_model_tool)
            else:
                close_visible = True

        self.close_action.visible = close_visible

        if len(managed_model_tools) == 0:
            return

        for model_factory in model_factories:
            model_template = self._resources.template_from_factory(
                    model_factory)

            for managed_model_tool in managed_model_tools:
                if managed_model_tool.handles(model_template):
                    managed_model = self._resources.managed_model_from_template(model_template)
                    self._publish_open(managed_model)
                    managed_model_tool.models.append(managed_model)

    def __tool_models_changed(self, change):
        """ Invoked when a tool's list of managed models changes. """

        for managed_model in change.old:
            observe('dirty', managed_model, self.__model_dirty_changed,
                    remove=True)

        for managed_model in change.new:
            observe('dirty', managed_model, self.__model_dirty_changed)

        self._update_dirty()

    def __model_dirty_changed(self, change):
        """ Invoked when a managed model's dirty state changes. """

        if change.new:
            self.dirty = True
        else:
            self._update_dirty()

    def _update_dirty(self):
        """ Update this tool's dirty state. """

        dirty = False

        for managed_model_tool in self._managed_model_tools():
            for managed_model in managed_model_tool.models:
                if managed_model.dirty:
                    dirty = True
                    break

        self.dirty = dirty

    def __tools_changed(self, change):
        """ Invoked when the list of tools changes. """

        for tool in change.old:
            managed_model_tool = IManagedModelTool(tool, exception=False)
            if managed_model_tool is not None:
                self._detach_tool(managed_model_tool)

        for tool in change.new:
            managed_model_tool = IManagedModelTool(tool, exception=False)
            if managed_model_tool is not None:
                self._attach_tool(managed_model_tool)

        self._update_resources()
        self._auto_new()

    def _attach_tool(self, managed_model_tool):
        """ Attach a managed model tool. """

        observe('models', managed_model_tool, self.__tool_models_changed)
        managed_model_tool.manager = self

    def _detach_tool(self, managed_model_tool):
        """ Detach a managed model tool. """

        managed_model_tool.manager = None
        observe('models', managed_model_tool, self.__tool_models_changed,
                remove=True)

    @observe('shell')
    def __shell_changed(self, change):
        """ Invoked when the shell changes. """

        # Remove from any old shell.
        shell = change.old
        if shell is not None:
            for managed_model_tool in self._managed_model_tools(shell):
                self._detach_tool(managed_model_tool)

            observe('tools', shell, self.__tools_changed, remove=True)
            observe('current_view', shell, self.__current_view_changed,
                    remove=True)

            observe('ready', IView(shell), self.__shell_ready, remove=True)

        # Add to any new shell.
        shell = change.new
        if shell is not None:
            for managed_model_tool in self._managed_model_tools(shell):
                self._attach_tool(managed_model_tool)

            self._update_resources()

            # Get the actions into a known state.
            self.close_action.enabled = False

            self.new_action.visible = self._resources.new_is_valid()

            self.open_action.visible = self._resources.open_is_valid()

            save_are_valid = self._resources.save_are_valid()

            self.save_action.visible = save_are_valid
            self.save_action.enabled = False

            self.save_as_action.visible = save_are_valid
            self.save_as_action.enabled = False

            observe('current_view', shell, self.__current_view_changed)
            observe('tools', shell, self.__tools_changed)

            observe('ready', IView(shell), self.__shell_ready)

    @close_action.triggered
    def close_action(self):
        """ Invoked when the Close action is triggered. """

        self.shell.close_view()

    @new_action.triggered
    def new_action(self):
        """ Invoked when the New action is triggered. """

        model_template = self._resources.only_model_template_for_new()

        if model_template is not None:
            # Get the tools.
            managed_model_tools = self._resources.tools_for_new(model_template)

            if len(managed_model_tools) > 1:
                # Ask for the tool.

                from .tool_dialog import ToolDialog

                dialog = ToolDialog(title=self.user_new_title,
                        model_manager=self, tools=tools)

                if not dialog.execute():
                    return

                managed_model_tool = dialog.tool
            else:
                # We know the tool.
                managed_model_tool = managed_model_tools[0]

        elif self._resources.are_multiple_tools_for_new():
            # We need to ask the user for both the model factory and tool.

            from .new_wizard import NewWizard

            wizard = NewWizard(title=self.user_new_title, model_manager=self)

            if not wizard.execute():
                return

            model_template = wizard.model_template
            managed_model_tool = wizard.tool

        else:
            # We will know the tool once we know the model template.

            from .model_template_dialog import ModelTemplateDialog

            dialog = ModelTemplateDialog(title=self.user_new_title,
                    model_manager=self)

            if not dialog.execute():
                return

            model_template = dialog.model_template

            managed_model_tools = self._resources.tools_for_new(model_template)
            managed_model_tool = managed_model_tools[0]

        if self._new_views_allowed(managed_model_tool):
            # Create an instance of the model and add it to the tool.
            managed_model = self._resources.managed_model_from_template(
                    model_template)
            self._publish_open(managed_model)
            managed_model_tool.models.append(managed_model)

    @open_action.triggered
    def open_action(self):
        """ Invoked when the Open action is triggered. """

        model_template, storage, managed_model_tool = self._resources.only_model_template_for_open()

        if model_template is None or storage is None or managed_model_tool is None:
            from .open_wizard import OpenWizard

            # FIXME: Should these wizards have a title? The macOS standard
            # dialogs don't. If other platforms don't then remove them from the
            # wizards.
            wizard = OpenWizard(title=self.user_open_title, model_manager=self,
                    location=self._default_location,
                    model_template=model_template, storage=storage,
                            tool=managed_model_tool)

            if not wizard.execute():
                return

            model_template = wizard.model_template
            location = wizard.location
            managed_model_tool = wizard.tool

        else:
            # We know everything except the location.
            location = storage.ui.get_read_location(self.user_open_title,
                    default_location=self._default_location,
                    hints=model_template, parent=self.shell)

            if location is None:
                return

        # Remember for the next dialog/wizard.
        self._default_location = location

        if not self._new_views_allowed(managed_model_tool):
            return

        # Create and read the model.
        managed_model = self._resources.managed_model_from_template(
                model_template)

        try:
            managed_model = self._read_managed_model(managed_model, location)
        except StorageError as e:
            Application.warning("Read Error",
                    "There was an error reading {0}.".format(
                            IDisplay(managed_model).name),
                    self.shell, str(e))

            return

        if managed_model is not None:
            self._publish_open(managed_model)
            managed_model_tool.models.append(managed_model)

    @save_action.triggered
    def save_action(self):
        """ Invoked when the Save action is triggered. """

        if not self._saveable(self.user_save_title):
            return

        self._save_managed_model(self._current_managed_model)

    @save_as_action.triggered
    def save_as_action(self):
        """ Invoked when the Save As action is triggered. """

        if not self._saveable(self.user_save_as_title):
            return

        managed_model = self._current_managed_model

        self._save_managed_model_as(managed_model)
        self.save_action.enabled = (managed_model.location is not None)

    def _save_managed_model_as(self, managed_model):
        """ Save a model at a new location. """

        default_location = managed_model.location
        if default_location is None:
            default_location = self._default_location

        location = IoManager.ui.writeable_storage_location(
                self.user_save_as_title, default_location=default_location,
                format=managed_model.native_format, hints=managed_model,
                parent=self.shell)

        if location is None:
            return

        self._default_location = managed_model.location = location

        self._save_managed_model(managed_model)

    def __current_view_changed(self, change):
        """ Invoked when the shell's current view changes. """

        self._current_managed_model_tool, self._current_managed_model = self._tool_model_from_view(change.new)

        enabled = (self._current_managed_model is not None)

        if enabled:
            close_enabled = (self._current_managed_model_tool.model_policy != 'one')
            save_enabled = (self._current_managed_model.location is not None)
        else:
            close_enabled = False
            save_enabled = False

        self.close_action.enabled = close_enabled
        self.save_action.enabled = save_enabled
        self.save_as_action.enabled = enabled

    def _new_views_allowed(self, managed_model_tool):
        """ Try and get things into a state where a new view will be allowed.
        """

        if managed_model_tool.model_policy != 'many':
            return self.shell.close_view(managed_model_tool.views[0])

        return self.shell.new_view_allowed()

    def _tool_model_from_view(self, view):
        """ Return the managed tool and model being handled by a view, if any.
        """

        if view is not None:
            for managed_model_tool in self._managed_model_tools():
                for managed_model in managed_model_tool.models:
                    if view in managed_model.views:
                        return managed_model_tool, managed_model

        # The view isn't of a managed model.  However if there is only one
        # managed model tool and it only has one model then we pretend it is
        # current as the actions won't be ambiguous.
        # TODO: Make this behaviour a property of the shell.
        tools = list(self._managed_model_tools())
        if len(tools) == 1 and len(tools[0].models) == 1:
            return tools[0], tools[0].models[0]

        return None, None

    @_resources.default
    def _resources(self):
        """ Invoked to return the default resources state. """

        return ResourcesState()

    def _update_resources(self):
        """ Update the internal state when the resources have changed. """

        if self.shell is None:
            return

        self._resources.update(self.model_factories, self.shell.tools)

        # Update the state of the dependent actions.
        self.new_action.visible = self._resources.new_is_valid()
        self.open_action.visible = self._resources.open_is_valid()
        self.save_action.visible = self.save_as_action.visible = self._resources.save_are_valid()

    def _saveable(self, title):
        """ Tell the use if the current model cannot be saved. """

        managed_model = self._current_managed_model

        if managed_model.invalid_reason == '':
            return True

        # Note that we don't tie the enabled state of the action to the invalid
        # reason.  This is so that we get the opportunity to tell the user why
        # the model cannot be saved.

        Application.warning(title, self._no_save_reason(managed_model),
                detail=managed_model.invalid_reason, parent=self.shell)

        return False

    def _save_managed_model(self, managed_model):
        """ Save a model. """

        location = managed_model.location

        try:
            location.storage.write(unadapted(managed_model), location)
        except StorageError as e:
            Application.warning("Write Error",
                    "There was an error writing {0}.".format(
                            IDisplay(managed_model).name),
                    self.shell, str(e))

            return

        managed_model.dirty = False

    def _managed_model_tools(self, shell=None):
        """ A generator for the managed model tools. """

        if shell is None:
            shell = self.shell

        for tool in shell.tools:
            managed_model_tool = IManagedModelTool(tool, exception=False)
            if managed_model_tool is not None:
                yield managed_model_tool

    @staticmethod
    def _no_close_reason(managed_model):
        """ Return the reason why a managed model should not be closed. """

        return "{0} has unsaved changes.".format(IDisplay(managed_model).name)

    @staticmethod
    def _no_save_reason(managed_model):
        """ Return the reason why a managed model cannot be closed. """

        return "{0} cannot be saved in its current state.".format(
                IDisplay(managed_model).name)

    def _read_managed_model(self, managed_model, location):
        """ Read a model from a location. """

        # Set the management data now so that the codec can update the dirty
        # flag if it wants to.
        managed_model.location = location
        managed_model.dirty = False

        read_model = location.storage.read(unadapted(managed_model), location)

        if read_model is None:
            managed_model = None
        elif read_model is not unadapted(managed_model):
            # Add the management data if the codec created its own model.
            read_managed_model = IManagedModel(read_model)
            read_managed_model.location = managed_model.location
            read_managed_model.dirty = managed_model.dirty

            managed_model = read_managed_model

        return managed_model

    def _publish_open(self, managed_model):
        """ Publish the opening of a model. """

        self.publication = Publication(model=unadapted(managed_model),
                event='dip.events.opened')

    def _publish_close(self, managed_model):
        """ Publish the closing of a model. """

        self.publication = Publication(model=unadapted(managed_model),
                event='dip.events.closed')
