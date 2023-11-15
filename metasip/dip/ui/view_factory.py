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


from ..model import Callable, MappingProxy, Model, Str, unadapted

from .toolkits import UIToolkit
from .i_view import IView


class ViewFactory(Model):
    """ The ViewFactory class is the base class for all factories that
    create views, sub-views and editors.
    """

    # The controller factory.  This must return a :class:`~dip.ui.Controller`
    # instance.
    controller_factory = Callable()

    # This is set if the view is enabled.
    enabled = IView.enabled

    # The view's identifier.  If it is not specified then a sub-class may
    # implement an appropriate default.
    id = Str()

    # The interface that the view can be adapted to.  Note that this is a class
    # attribute.
    interface = IView

    # The status tip.
    status_tip = IView.status_tip

    # The short, user friendly title of the view.  It may be used by different
    # views in different ways, for example a form may use it as a field label,
    # or a push button may use it as the text of the button.  If the view is a
    # top-level window then it is used as the window title and may include the
    # marker '[*]' which will be replaced by some, platform specific,
    # indication of the application's overall dirty state.
    title = IView.title

    # The tool tip.
    tool_tip = IView.tool_tip

    # The name of the toolkit factory method.
    toolkit_factory = Str()

    # The registered view factories.  Note that this is a class attribute.
    view_factories = []

    # This is set if the view is visible.
    visible = IView.visible

    # The "What's This?" help.
    whats_this = IView.whats_this

    def __init__(self, **properties):
        """ Initialize the factory.

        :param properties:
            are keyword arguments used as property names and values that are
            applied to each toolkit view created by the factory.
        """

        self._properties = properties

    def __call__(self, model=None, parent=None, top_level=True):
        """ Create a view and bind it to a model and optional controller.

        :param model:
            is the optional model which is either a :class:`~dip.model.Model`
            instance or a Python mapping object.
        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        # Make sure we have a Model for the model.
        if model is None:
            model = Model()
        elif not isinstance(model, Model):
            model = MappingProxy(model)

        # Create the view.
        view = self.create_view(model, parent, None, top_level)

        # Make any sub-view and actions with an id visible as an attribute of
        # the top-level view.
        self.expose_views(view)

        # FIXME: may need a toolkit-specific renderer for QML.

        # Create the controller.
        controller = self.controller_factory(model=model, view=view)

        # Update the view according to the current state of the model.
        controller.refresh_view()

        return view

    def create_view(self, model, parent, root, top_level=False):
        """ Create the view instance.

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

        view = self.interface(
                getattr(UIToolkit, self.toolkit_factory)(parent, top_level))

        self.configure_view(view, model)

        return view

    def configure_view(self, view, model):
        """ Configure a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        self.initialise_view(view, model)
        self.finalise_view(view)

    @classmethod
    def expose_item(cls, view, item):
        """ Expose an item with an id as a attribute of a top-level view.

        :param view:
            is the top-level view.
        :param item:
            is the item (normally a view or an action) to expose.
        """

        if item is view:
            return

        # Allow for dot-separated ids.
        id = item.id.replace('.', '_')

        if id != '':
            # Don't blindly replace existing attributes.
            if hasattr(view, id):
                raise ValueError(
                        "view {0} already has an attribute '{1}'".format(view,
                                id))

            setattr(view, id, item)

    @classmethod
    def expose_views(cls, view):
        """ Expose the sub-views with an id as a attribute of a top-level view.

        :param view:
            is the top-level view.
        """

        for v in view.all_views():
            cls.expose_item(view, v)

    def finalise_view(self, view):
        """ Finalise the configuration of a view instance.

        :param view:
            is the view.
        """

        # Make sure the title has a value.
        if view.title == '':
            title = self.get_natural_name(self.id)
            if title == '':
                # The last resort that should give a hint to provide a title.
                title = str(unadapted(view))

            view.title = title

        # Apply any toolkit-specific properties.
        view.configure(self._properties)

    @staticmethod
    def get_natural_name(name):
        """ Convert a name, typically of an attribute, to a more natural name.

        :param name:
            is the original name.
        :return:
            the more natural version.
        """

        name = name.strip()

        if name != '':
            name = name.replace('_', ' ')
            name = name[0].upper() + name[1:]

        return name

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        view.id = self.id

        view.enabled = self.enabled
        view.factory = self
        view.status_tip = self.status_tip
        view.title = self.title
        view.tool_tip = self.tool_tip
        view.whats_this = self.whats_this

        # Only set the visibility if it has been explicitly set to False.  This
        # means we don't intefere with how the actual state is determined by
        # the toolkit view's parent.  We also allow for a value of None which
        # some container factories interpret as visible only if there are
        # visible contents.
        if self.visible is False:
            view.visible = False

    @controller_factory.default
    def controller_factory(self):
        """ Invoked to return the default controller factory. """

        from .controller import Controller

        return Controller
