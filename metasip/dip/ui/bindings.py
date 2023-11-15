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


from ..model import (Callable, get_attribute_type, MappingProxy, Model,
        resolve_attribute_path)

from .i_editor import IEditor
from .editor_factory import EditorFactory
from .toolkits import UIToolkit
from .i_view import IView
from .view_factory import ViewFactory


class Bindings(Model):
    """ The Bindings class represents set of bindings between widgets of a user
    interface and attributes of a model.
    """

    # The controller factory.  This must return a :class:`~dip.ui.Controller`
    # instance.
    controller_factory = Callable()

    def __init__(self, **bindings):
        """ Initialise the bindings.

        :param bindings:
            the bindings specified as keyword arguments.  The argument name is
            the object name of the widget that the attribute will be bound to.
            The argument value is the binding.  If the argument value is a
            string then an :class:`~dip.ui.EditorFactory` instance will be
            automatically created for it.
        """

        self._bindings = bindings

    def bind(self, toolkit_view, model):
        """ Bind a view to a model.

        :param toolkit_view:
            is the toolkit-specific view.
        :param model:
            is the model which is either a :class:`~dip.model.Model` instance
            or a Python mapping object.
        """

        # Make sure we have a Model for the model.
        if not isinstance(model, Model):
            model = MappingProxy(model)

        # Make sure we have the view as a toolkit object and its adapted form.
        view = self.__view_from_toolkit_view(toolkit_view)
        view.configure({})

        for view_name, itm in self._bindings.items():
            # Find the sub-view in the user interface.
            toolkit_subview = UIToolkit.find_toolkit_view(toolkit_view,
                    view_name)
            subview = self.__view_from_toolkit_view(toolkit_subview)

            # Automatically create a factory if needed.
            if isinstance(itm, EditorFactory):
                name = itm.bind_to
                subview_factory = itm
            elif isinstance(itm, ViewFactory):
                name = None
                subview_factory = itm
            elif isinstance(itm, str):
                name = itm

                # Create a view factory for the subview.
                subview_factory_factory = self.__factory_for_view(subview)
                subview_factory = subview_factory_factory(itm, id=view_name)
            else:
                raise TypeError(
                        "the binding for '{0}' must be either an instance of "
                        "a ViewFactory sub-class or a string, not "
                        "'{1}'".format(view_name, type(itm).__name__))

            # Update the factory with the subview's name so that it doesn't get
            # changed when the toolkit subview is configured.
            subview_factory.id = view_name

            subview.factory = subview_factory

            if isinstance(subview, IEditor):
                attr_name, attr_model = resolve_attribute_path(name, model)
                attr_type = get_attribute_type(attr_model, attr_name)

                subview.attribute_name = attr_name
                subview.attribute_type = attr_type
                subview.model = attr_model

            subview_factory.configure_view(subview, model)

        # Expose the sub-views.
        ViewFactory.expose_views(view)

        # Create the controller.
        controller = self.controller_factory(model=model, view=view)

        # Update the view according to the current state of the model.
        controller.refresh_view()

    @controller_factory.default
    def controller_factory(self):
        """ Invoked to return the default controller factory. """

        from .controller import Controller

        return Controller

    @staticmethod
    def __view_from_toolkit_view(toolkit_view):
        """ Return the view for a toolkit view. """

        for factory in ViewFactory.view_factories:
            view = factory.interface(toolkit_view, exception=False)
            if view is not None:
                return view

        return IView(toolkit_view)

    @staticmethod
    def __factory_for_view(view):
        """ Return the factory for the factory that would create a view. """

        for factory in ViewFactory.view_factories:
            if isinstance(view, factory.interface):
                return factory

        raise TypeError(
                "there is no editor factory that creates instances of {0}".format(
                        type(view).__name__))
