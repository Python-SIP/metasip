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


from ..model import Callable, Enum, List, Str
from ..ui import ViewFactory

from .i_shell import IShell


class BaseShellFactory(ViewFactory):
    """ The BaseShellFactory class is a base class for shell factories.  It
    creates views that can be adapted to the :class:`~dip.shell.IShell`
    interface.
    """

    # The identifier of a shell.
    id = 'dip.shell'

    # This determines how multiple views placed in the main area of the shell
    # are handled.  'multiple' means that the area may contain any number of
    # views and will visualise the area in the same way irrespective of the
    # number of views.  'on_demand' means that the area may contain any number
    # of views but it may visualise the area differently if it contains a
    # single view.  'single' means that the area may only ever contain one view
    # and an old view must be discarded before a new view is added.
    main_area_policy = Enum('multiple', 'on_demand', 'single')

    # The template from which the window title is derived.  Tokens in the
    # template are replaced by their corresponding values:
    #
    # [view] is replaced by the :attr:`~dip.ui.IDisplay.name` of the active
    # view.
    #
    # Note that, as with :attr:`~dip.ui.IView.title`, [*] will be replaced with
    # the application modification state by the toolkit.
    title_template = Str()

    # The tool factories.  A factory should return an object that implements or
    # can be adapted to :class:`~dip.shell.ITool`.
    tool_factories = List(Callable())

    def create_view(self, model, parent, root, top_level=False):
        """ Create the shell view instance.

        :param model:
            is the model.
        :param parent:
            is the optional parent view.
        :param root:
            is the optional root view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view which can be adapted to the :class:`~dip.shell.IShell`
            interface.
        """

        view = self.create_shell(model, parent, top_level)

        shell = IShell(view)

        shell.main_area_policy = self.main_area_policy
        shell.title_template = self.title_template

        # Add any initial tools.
        shell.tools = [factory() for factory in self.tool_factories]

        self.configure_view(view, model)

        return view

    def create_shell(self, model, parent, top_level):
        """ Create the view that implements the shell.  This should be
        reimplemented by a sub-class.

        :param model:
            is the model.
        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the shell.
        """

        raise NotImplementedError
