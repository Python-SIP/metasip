# Copyright (c) 2023 Riverbank Computing Limited.
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


from ..model import (Bool, Callable, get_attribute_type, get_model_types, List,
        resolve_attribute_path)

from .i_action import IAction
from .i_container import IContainer
from .toolkits import UIToolkit
from .view_factory import ViewFactory


class ContainerFactory(ViewFactory):
    """ The ContainerFactory class is the base factory class for all views that
    can contain sub-views.  A sub-class determines the layout of the sub-views.
    """

    # The list of action factories.  Each is called with the model as arguments
    # and must return an object that implements or can be adapted to either the
    # :class:`~dip.ui.IAction` or :class:`~dip.ui.IActionCollection`
    # interfaces.
    actions = List(Callable())

    # This is ``True`` if the contents should be automatically populated from
    # a model's attribute types (if no contents where explicitly set).
    auto_populate = Bool(False)

    # The contents of the view.
    contents = List()

    def __init__(self, *contents, **properties):
        """ Initialise the factory.

        :param contents:
            is the list of the view's contents.  An individual item can either
            be a :class:`~dip.ui.ViewFactory` instance or a string.  Strings
            are are assumed to be the names of attributes within a model.  Such
            names may include one or more periods to specify an
            :term:`attribute path`.
        :param properties:
            are keyword arguments used as property names and values that are
            applied to each toolkit view created by the factory.
        """

        super().__init__(**properties)

        self.contents = contents

    def create_view(self, model, parent, root, top_level=False):
        """ Create a view instance.

        :param model:
            is the model.
        :param parent:
            is the optional parent view.
        :param root:
            is the optional root view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        view = super().create_view(model, parent, root, top_level)

        # See if this is the root view.
        if root is None:
            root = view

        # Create any sub-views.
        view.views = self.create_subviews(model, view, root)

        return view

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        # Create any actions.
        for action_factory in self.actions:
            view.actions.append(IAction(action_factory(model)))

    def create_subviews(self, model, view, root):
        """ Create the sub-views for a containing view.

        :param model:
            is the model.
        :param view:
            is the containing view.
        :param root:
            is the optional root view.
        :return:
            the sub-views.
        """

        # Go through the contents invoking the corresponding factories.
        subviews = []

        # If there are no explicit contents then inspect any model.
        contents = self.contents

        if len(contents) == 0 and self.auto_populate:
            contents = get_model_types(type(model)).keys()

        for content in contents:
            if isinstance(content, str):
                name, submodel = resolve_attribute_path(content, model)
                attribute_type = get_attribute_type(submodel, name)

                # Create an editor factory based on the type.
                editor_factory_factory = UIToolkit.declarative_factory_for_attribute_type(attribute_type)
                editor_factory = editor_factory_factory(content)
                subview = editor_factory.create_view(model, view, root)

            elif isinstance(content, ViewFactory):
                subview = content.create_view(model, view, root)

            else:
                subview = self.create_additional_content(content)

            subviews.append(subview)

        return subviews

    def create_additional_content(self, content):
        """ Create additional content to be added to the list of sub-views.
        This default implementation will always raise an exception.

        :param content:
            the content from which additional content can be created.
        :return:
            the additional content.
        """

        raise TypeError("the contents of a view must be either an instance of "
                "a ViewFactory sub-class or a string, not "
                "'{0}'".format(type(content).__name__))

    @classmethod
    def expose_item(cls, view, item):
        """ Expose an item with an id as a attribute of a top-level view.

        :param view:
            is the top-level view.
        :param item:
            is the item (normally a view or an action) to expose.
        """

        # Do the view.
        super().expose_item(view, item)

        # Do any actions.
        if isinstance(item, IContainer):
            for action in item.actions:
                super().expose_item(view, action)
