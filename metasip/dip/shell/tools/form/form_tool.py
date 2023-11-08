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


from ....model import Callable, implements, Instance, observe, Str
from ....ui import ViewFactory

from ... import (IAreaHints, BaseManagedModelTool, IManagedModel,
        IManagedModelTool)


@implements(IManagedModelTool)
class FormTool(BaseManagedModelTool):
    """ The FormTool class is a :term:`tool` that uses an automatically
    generated :term:`view` (a :class:`~dip.ui.Form` by default) to manipulate a
    :term:`managed model`.
    """

    # The identifier of the area where the view should be placed.
    area = Str()

    # The controller factory.  This must return a :class:`~dip.ui.Controller`
    # instance.
    controller_factory = Callable()

    # The type of model that the tool can handle.
    model_type = Instance(type)

    # The factory used to create the tool's views.
    view_factory = Instance(ViewFactory)

    def create_views(self, model):
        """ Create the views for a managed model.

        :param model:
            is the model.
        :return:
            the list of views.
        """

        view_factory = self.view_factory

        if self.controller_factory is not None:
            view_factory.controller_factory = self.controller_factory

        view = self.view_factory(model, top_level=False)

        # Initialise the invalid reason.
        IManagedModel(model).invalid_reason = view.controller.invalid_reason

        # Handle future changes.
        def update_invalid_reason(change):
            IManagedModel(model).invalid_reason = change.new

        observe('invalid_reason', view.controller, update_invalid_reason)

        # Maintain the dirty state.
        def update_dirty(change):
            IManagedModel(model).dirty = True

        observe('*', model, update_dirty)

        # Position the view.
        IAreaHints(view).area = self.area

        return [view]

    def handles(self, model):
        """ Check if the tool can handle a particular model.

        :param model:
            is the model.
        :return:
            ``True`` if a tool can handle the model.
        """

        return isinstance(model, self.model_type)

    @view_factory.default
    def view_factory(self):
        """ Invoked to return the default view factory. """

        from ....ui import Form

        return Form()
