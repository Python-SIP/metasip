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


from ..model import Adapter, implements, Instance, Model, observe, unadapted
from ..publish import Publication, IPublisher
from ..ui import IDisplay, IView

from .i_close_view_veto import ICloseViewVeto
from .i_managed_model import IManagedModel
from .i_open_model import IOpenModel


@implements(ICloseViewVeto, IPublisher, IOpenModel)
class BaseManagedModelTool(Model):
    """ The BaseManagedModelTool class is a base class for :term:`tools<tool>`
    that handle :term:`managed models<managed model>`.  It automatically manages
    the different lists of views and provides a convenient interface to the
    changing of the active view and model.
    """

    # The active model, if any.
    _active_model = Instance(IManagedModel)

    def create_views(self, model):
        """ Create the views for a managed model.

        This must be implemented by a sub-class.

        :param model:
            is the model.
        :return:
            the list of views.
        """

        raise NotImplementedError

    def veto(self, view):
        """ Determine if the view is to be prevented from being closed.

        :param view:
            is the view.
        :return:
            ``True`` if the close of the view is to be prevented.
        """

        return self.manager.veto_close_view(view, self)

    def open_model(self, location):
        """ Open a model at a storage location.

        :param location:
            is the storage location.
        """

        self.manager.open_model(location, self)

    @observe('models')
    def __models_changed(self, change):
        """ Invoked when the list of the tool's models changes. """

        # This will take care of the same model being handled by multiple
        # tools.
        for model in change.old:
            if model is self._active_model:
                self._deactivate_model()

            observe('name', IDisplay(model), self.__model_name_changed,
                    remove=True)

            for view in model.views:
                # Remove from the tool before removing from the shell.
                self.views.remove(view)
                self.shell.views.remove(view)

            model.views = []

        for model in change.new:
            views = [IView(v) for v in self.create_views(unadapted(model))]

            # Each view takes the name of the model.
            idisplay = IDisplay(model)

            for view in views:
                view.title = idisplay.name

            model.views.extend(views)
            self.views.extend(views)
            self.shell.views.extend(views)

            observe('name', idisplay, self.__model_name_changed)

    @observe('current_view')
    def __current_view_changed(self, change):
        """ Invoked when the tool's current view changes. """

        view = change.new

        # Find the model.
        if view is None:
            model = None
        else:
            for model in self.models:
                if view in model.views:
                    break
            else:
                model = None

        # See if the active model has changed.
        if self._active_model is not model:
            if self._active_model is not None:
                self._deactivate_model()

            if model is not None:
                self._active_model = model
                self.publication = Publication(model=unadapted(model),
                        event='dip.events.active')

    def _deactivate_model(self):
        """ Publish the deactivation of any active model. """

        self.publication = Publication(model=unadapted(self._active_model),
                event='dip.events.inactive')
        self._active_model = None

    def __model_name_changed(self, change):
        """ Invoked when the name of a model changes. """

        idisplay = change.model

        for view in IManagedModel(idisplay).views:
            view.title = idisplay.name
