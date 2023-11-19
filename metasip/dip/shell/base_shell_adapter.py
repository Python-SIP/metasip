# Copyright (c) 2018 Riverbank Computing Limited.
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


#from ..io import IoManager
from ..model import Adapter, get_attribute_types, observe
from ..publish import IPublisher, ISubscriber
from ..ui import Action, ActionCollection, Application, IContainer, IView

from .i_area_hints import IAreaHints
from .i_close_view_veto import ICloseViewVeto
from .i_open_model import IOpenModel
from .i_shell import IShell


class BaseShellAdapter(Adapter):
    """ The BaseShellAdapter class is a base class for adapters to the IShell
    interface.  It implements housekeeping common to all shells.
    """

    def __init__(self):
        """ Initialise the adapter. """

        observe('active_view', Application(), self.__active_view_changed)

        super().__init__()

    def close_view(self, view=None):
        """ Close a view if possible.

        :param view:
            is the view.  If it is not specified then the current view is
            closed.
        :return:
            ``True`` if the view was closed.
        """

        if view is None:
            view = self.current_view

        # Find the tool containing the view.
        for tool in self.tools:
            if view in tool.views:
                icloseviewveto = ICloseViewVeto(tool, exception=False)

                if icloseviewveto is None:
                    tool.views.remove(view)
                    self.views.remove(view)
                    closed = True
                else:
                    closed = not icloseviewveto.veto(view)

                if closed and view is self.current_view:
                    self.current_view = None

                return closed

        # We should never get here.
        return False

    def new_view_allowed(self):
        """ This determines if the main area policy allows for a new view to
        be added.

        :return:
            ``True`` if a new view is allowed.
        """

        # Handle the trivial case.
        if self.main_area_policy != 'single':
            return True

        # See if there is already a view in the main area.
        for view in self.views:
            if IAreaHints(view).area == '':
                # Try and close it.
                return self.close_view(view)

        return True

    def open(self, tool_id, location, format=''):
        """ Open the model at a location and add it to a tool.

        :param tool_id:
            is the identifier of the tool to handle the model.
        :param location:
            is the location as a string.
        :param format:
            is the identifier of the optional format.
        """

        # Get the tool.
        for tool in self.tools:
            if tool.id == tool_id:
                break
        else:
            raise ValueError(
                    "there is no tool with the identifier '{0}'".format(
                            tool_id))

        # Convert the location to a list of storage location instances.
        locations = IoManager.readable_locations_from_string(location, format)

        nr_locations = len(locations)

        if nr_locations == 0:
            Application.warning("Open",
                    "{0} is not a valid readable storage location.".format(
                            location), self.adaptee)
            return

        if nr_locations > 1:
            # Note that this is really a badly configured application.
            Application.warning("Open",
                    "{0} is an ambiguous readable storage location.".format(
                            location), self.adaptee)
            return

        # Ask the tool to open the model.
        IOpenModel(tool).open_model(locations[0])

    @IShell.publication_manager.default
    def publication_manager(self):
        """ Invoked to return the default publication manager. """

        from ..publish.default_publication_manager import PublicationManager

        return PublicationManager()

    @observe('tools')
    def __tools_changed(self, change):
        """ Invoked when the list of tools changes. """

        view = IView(self.adaptee)

        # Unbind the shell from any old tools.
        for tool in change.old:
            if isinstance(tool, IPublisher):
                self.publication_manager.publishers.remove(tool)

            if isinstance(tool, ISubscriber):
                self.publication_manager.subscribers.remove(tool)

            if isinstance(view, IContainer):
                for action in tool.actions:
                    view.actions.remove(action)

            for tool_view in tool.views:
                self.views.remove(tool_view)

            tool.shell = None

        # Bind the shell to any new tools.
        for tool in change.new:
            tool.shell = self

            for tool_view in tool.views:
                self.views.append(tool_view)

            if len(tool.actions) == 0:
                tool.actions = get_attribute_types(tool, ActionCollection)
                tool.actions.extend(get_attribute_types(tool, Action))

            if isinstance(view, IContainer):
                view.actions.extend(tool.actions)

            if isinstance(tool, ISubscriber):
                self.publication_manager.subscribers.append(tool)

            if isinstance(tool, IPublisher):
                self.publication_manager.publishers.append(tool)

    @observe('views')
    def __views_changed(self, change):
        """ Invoked when the list of views changes. """

        for view in change.old:
            observe('title', view, self.__view_title_changed,
                    remove=True)

        for view in change.new:
            observe('title', view, self.__view_title_changed)

    def __view_title_changed(self, change):
        """ Invoked when the title of a view changes. """

        self._update_title(change.new)

    def _update_title(self, view_title):
        """ Update the shell's title when the title of a view changes. """

        if self.title_template != "":
            IView(self.adaptee).title = self.title_template.replace('[view]',
                    view_title)

    def __active_view_changed(self, change):
        """ Invoked when the active view changes. """

        # Only update the current view if the active view is in one of the
        # shell's views.  This means that the current view will not change when
        # the application is not active.
        active_view = change.new

        if active_view is None:
            # However if there is no active view because our last view has been
            # closed then reset the current view.
            no_views = True
            for tool in self.tools:
                if len(tool.views) == 0:
                    tool.current_view = None
                else:
                    no_views = False

            if no_views:
                self.current_view = None
        else:
            for tool in self.tools:
                for view in tool.views:
                    if self._container_has_view(view, active_view):
                        # Reset the current tool of all other tools.
                        for reset_tool in self.tools:
                            if reset_tool is not tool:
                                reset_tool.current_view = None

                        tool.current_view = self.current_view = view

                        # Update the title if there is a template.
                        self._update_title(view.title)

                        return

    @classmethod
    def _container_has_view(cls, container, view):
        """ See if a (possible) container contains a view. """

        if container is view:
            return True

        if isinstance(container, IContainer):
            for subview in container.views:
                if cls._container_has_view(subview, view):
                    return True

        return False
