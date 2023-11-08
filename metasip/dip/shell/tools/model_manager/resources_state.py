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


from ....io import IoManager
from ....model import Bool, Dict, Instance, Model
from ....ui import IDisplay

from ... import IManagedModel, IManagedModelTool


class _ModelTemplateMap(Model):
    """ An internal class that defines the relationships between all available
    models factories and dependent resources.
    """

    # This is set if at least one model template has more than one dependent
    # resource.  In other words there is at least one value in the 'map' dict
    # whose length is >= 1.
    multi = Bool(False)

    # The list of dependent resources associated with each model template.
    map = Dict()


class ResourcesState(Model):
    """ An internal class that encapsulates the relationships between the
    different object, tool and storage resources.
    """

    # The model factories keyed by the corresponding model template.  A model
    # template is just an instance of the model.  This means that models should
    # be lightweight objects (and/or use the mechanism for lazily initialising
    # attributes).  We could use a system based on model types but (given the
    # use made of adaptation to interfaces) we would need to change issubclass
    # to take available adapter factories into account.
    _model_factories = Dict()

    # The storage for the Open action.
    _storage_for_open = Instance(_ModelTemplateMap)

    # The storage for the Save and Save As actions.
    _storage_for_save = Instance(_ModelTemplateMap)

    # The tools for the New action.
    _tools_for_new = Instance(_ModelTemplateMap)

    # The tools for the Open action.
    _tools_for_open = Instance(_ModelTemplateMap)

    def update(self, model_factories, tools):
        """ Update the state of the resources. """

        self._model_factories = {}
        self._tools_for_new = new_tools = _ModelTemplateMap()
        self._tools_for_open = open_tools = _ModelTemplateMap()
        self._storage_for_open = open_storage = _ModelTemplateMap()
        self._storage_for_save = save_storage = _ModelTemplateMap()

        for model_factory in model_factories:
            model_template = model_factory()
            self._model_factories[model_template] = model_factory

            new_tools_for_model_template = []
            open_tools_for_model_template = []

            for tool in tools:
                managed_model_tool = IManagedModelTool(tool, exception=False)
                if managed_model_tool is None:
                    continue

                if managed_model_tool.handles(model_template):
                    if managed_model_tool.new_tool:
                        new_tools_for_model_template.append(managed_model_tool)

                    if managed_model_tool.open_tool:
                        open_tools_for_model_template.append(managed_model_tool)

            nr_new_tools = len(new_tools_for_model_template)

            if nr_new_tools > 0:
                new_tools.map[model_template] = new_tools_for_model_template

                if nr_new_tools > 1:
                    new_tools.multi = True

            nr_open_tools = len(open_tools_for_model_template)

            if nr_open_tools > 0:
                native_format = IManagedModel(model_template).native_format

                storage_for_model_template = IoManager.readable_storage(
                        native_format)

                nr_storage = len(storage_for_model_template)

                if nr_storage > 0:
                    open_tools.map[model_template] = open_tools_for_model_template

                    if nr_open_tools > 1:
                        open_tools.multi = True

                    open_storage.map[model_template] = storage_for_model_template

                    if nr_storage > 1:
                        open_storage.multi = True

                if nr_new_tools > 0:
                    storage_for_model_template = IoManager.writeable_storage(
                            native_format)

                    nr_storage = len(storage_for_model_template)

                    if nr_storage > 0:
                        save_storage.map[model_template] = storage_for_model_template

                        if nr_storage > 1:
                            save_storage.multi = True

    def only_model_template_for_new(self):
        """ Return the only model template that has at least one tool that can
        handle it.  If there is more than one then None is returned.
        """

        if len(self._tools_for_new.map) == 1:
            return tuple(self._tools_for_new.map.keys())[0]

        return None

    def only_model_template_for_open(self):
        """ Return a 3-tuple of the only valid model template, storage and tool
        combination.  Any element may be None meaning that more than one
        combination is valid.
        """

        if len(self._tools_for_open.map) != 1:
            return None, None, None

        model_template = tuple(self._tools_for_open.map.keys())[0]

        storage_list = self._storage_for_open.map[model_template]
        storage = storage_list[0] if len(storage_list) == 1 else None

        managed_model_tools = self._tools_for_open.map[model_template]
        managed_model_tool = managed_model_tools[0] if len(managed_model_tools) == 1 else None

        return model_template, storage, managed_model_tool

    def model_templates_for_new(self):
        """ Return the sequence of model templates available to the New action.
        """

        return self._templates_and_labels(self._tools_for_new)

    def model_templates_for_open(self):
        """ Return the sequence of model templates available to the Open
        action.
        """

        # We could use the storage instead - the result is the same.
        return self._templates_and_labels(self._tools_for_open)

    def are_multiple_tools_for_new(self):
        """ Return True if there is a model template with multiple tools for new
        models.
        """

        return self._tools_for_new.multi

    def are_multiple_tools_for_open(self):
        """ Return True if there is a model template with multiple tools for
        existing models.
        """

        return self._tools_for_open.multi

    def are_multiple_storage_for_open(self):
        """ Return True if there is a model template with multiple storage
        instances for existing models.
        """

        return self._storage_for_open.multi

    def tools_for_new(self, model_template):
        """ Return the sequence of tools that can handle the given model
        template.
        """

        return self._tools_for_new.map[model_template]

    def tools_for_open(self, model_template):
        """ Return the sequence of tools that can handle the given model
        template.
        """

        return self._tools_for_open.map[model_template]

    def storage_for_open(self, model_template):
        """ Return the sequence of storage instances that can handle a model
        template.
        """

        return self._storage_for_open.map[model_template]

    def new_is_valid(self):
        """ Return True if the New action is valid. """

        return len(self._tools_for_new.map) > 0

    def open_is_valid(self):
        """ Return True if the Open action is valid. """

        # We could check the storage instead - the result is the same.
        return len(self._tools_for_open.map) > 0

    def save_are_valid(self):
        """ Return True if the Save and Save As actions are valid. """

        return len(self._storage_for_save.map) > 0

    def managed_model_from_template(self, model_template):
        """ Return a managed model from a template. """

        return IManagedModel(self._model_factories[model_template]())

    def template_from_factory(self, model_factory):
        """ Return the model template created by the given factory. """

        for model_template, factory in self._model_factories.items():
            if factory is model_factory:
                return model_template

        # This should never happen.
        return None

    def model_templates(self):
        """ Return the model templates. """

        return self._model_factories.keys()

    def _templates_and_labels(self, model_template_map):
        """ Return parallel lists of model templates and labels for a map. """

        model_templates = []
        labels = []

        for model_template in model_template_map.map.keys():
            model_templates.append(model_template)

            model_factory = self._model_factories[model_template]
            idisplay = IDisplay(model_factory, exception=False)
            label = idisplay.name if idisplay is not None else ''
            if label == '':
                label = str(model_factory)

            labels.append(label)

        return model_templates, labels
