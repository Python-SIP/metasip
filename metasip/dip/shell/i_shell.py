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


from ..model import Enum, Instance, Interface, List, Str
from ..publish import IPublicationManager
from ..ui import IView

from .i_tool import ITool


class IShell(Interface):
    """ The IShell interface defines the API of a :term:`shell`.

    The following action identifiers are considered to be well known.  A shell
    would normally be expected to honour them.

        dip.ui.actions.close
        dip.ui.actions.export
        dip.ui.actions.import
        dip.ui.actions.new
        dip.ui.actions.open
        dip.ui.actions.quit
        dip.ui.actions.save
        dip.ui.actions.save_as
        dip.ui.actions.whats_this

    The following action collection identifiers are considered to be well
    known.  A shell, if it supports the concept of action collections, would
    normally be expected to honour them.

        dip.ui.collections.edit
        dip.ui.collections.file
        dip.ui.collections.help
        dip.ui.collections.print
        dip.ui.collections.tools
        dip.ui.collections.undo
        dip.ui.collections.view

    The following area identifiers, used to position views, are defined.  A
    shell may interpret these in any way.  An empty string implies the main
    area.

        dip.shell.areas.left
        dip.shell.areas.right
        dip.shell.areas.bottom
        dip.shell.areas.top
    """

    # The current view.  It is not necessarily the active view.
    current_view = Instance(IView)

    # This determines how multiple views placed in the main area of the shell
    # are handled.  'multiple' means that the area may contain any number of
    # views and will visualise the area in the same way irrespective of the
    # number of views.  'on_demand' means that the area may contain any number
    # of views # but it may visualise the area differently if it contains a
    # single view.  'single' means that the area may only ever contain one view
    # and an old view must be discarded before a new view is added.
    main_area_policy = Enum('multiple', 'on_demand', 'single')

    # The publication manager.
    publication_manager = Instance(IPublicationManager)

    # The template from which the window title is derived.  Tokens in the
    # template are replaced by their corresponding values:
    #
    # [view] is replaced by the :attr:`~dip.ui.IDisplay.name` of the active
    # view.
    #
    # Note that, as with :attr:`~dip.ui.IView.title`, [*] will be replaced with
    # the application modification state by the toolkit.
    title_template = Str()

    # The list of the shell's tools.
    tools = List(ITool)

    # The list of the shell's views.
    views = List(IView)

    def close_view(self, view=None):
        """ Close a view if possible.

        :param view:
            is the view.  If it is not specified then the current view is
            closed.
        :return:
            ``True`` if the view was closed.
        """

    def new_view_allowed(self):
        """ This determines if the main area policy allows for a new view to
        be added.

        :return:
            ``True`` if a new view is allowed.  If not then the user will be
            informed.
        """

    def open(self, tool_id, location, format=''):
        """ Open the model at a location and add it to a tool.

        :param tool_id:
            is the identifier of the tool to handle the model.
        :param location:
            is the location as a string.
        :param format:
            is the identifier of the optional format.
        """
