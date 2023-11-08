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


from ..model import Callable, List

from .i_tool import ITool


class IModelManagerTool(ITool):
    """ The IModelManagerTool interface defines the API made available to
    implementations of the :class:`~dip.shell.IManagedModelTool` interface.
    """

    # The managed model factories.  A factory should return an object that
    # implements or can be adapted to :class:`~dip.shell.IManagedModel`.  If an
    # application may include more than one model type then the factory should
    # implement the :class:`~dip.ui.IDisplay` interface.
    model_factories = List(Callable())

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

    def open_model(self, location, tool):
        """ This handles :meth:`~dip.shell.IOpenModel.open_model` on behalf of
        an implementation of the :class:`~dip.shell.IManagedModelTool`
        interface.

        :param location:
            is the storage location.
        :param tool:
            is the tool.
        """
