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


from ..model import adapt, Adapter, notify_observers, observe
from ..ui import IDisplay

from .i_managed_model import IManagedModel


@adapt(IManagedModel, to=IDisplay)
class IManagedModelIDisplayAdapter(Adapter):
    """ Adapt IManagedModel to IDisplay using the model's location. """

    def __init__(self):
        """ Initialise the adapter. """

        observe('location', IManagedModel(self.adaptee),
                self.__location_changed)

    @IDisplay.name.getter
    def name(self):
        """ Invoked to get the name. """

        return self._model_name(IManagedModel(self.adaptee).location)

    @IDisplay.short_name.getter
    def short_name(self):
        """ Invoked to get the short name. """

        return self._model_short_name(IManagedModel(self.adaptee).location)

    def __location_changed(self, change):
        """ Invoked when the model's location changes. """

        notify_observers('name', self, self._model_name(change.new),
                self._model_name(change.old))

        notify_observers('short_name', self,
                self._model_short_name(change.new),
                self._model_short_name(change.old))

    @staticmethod
    def _model_name(location):
        """ Return the name derived from the given location. """

        return "Unnamed" if location is None else IDisplay(location).name

    @staticmethod
    def _model_short_name(location):
        """ Return the short name derived from the given location. """

        return "" if location is None else IDisplay(location).short_name
