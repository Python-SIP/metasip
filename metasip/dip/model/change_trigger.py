# Copyright (c) 2017 Riverbank Computing Limited.
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


# FIXME: replace with proper toolkit support.
from .. import TOOLKIT
if TOOLKIT == 'qt4':
    from PyQt4.QtCore import pyqtSignal, QCoreApplication, QObject
else:
    from PyQt5.QtCore import pyqtSignal, QCoreApplication, QObject


class ChangeTrigger(QObject):
    """ The ChangeTrigger class communicates a change on behalf of a particular
    instance of an attribute.  This is not part of the public API.
    """

    # The signal that is emitted when an attribute is changed.
    changed = pyqtSignal(object)

    def __init__(self):
        """ Initialize the instance. """

        super().__init__(QCoreApplication.instance())

        self._nr_observers = 0

    def add_observer(self, observer):
        """ Add an observer of this change. """

        self._nr_observers += 1
        self.changed.connect(observer)

    @property
    def change(self):
        """ The getter for a change. """

        raise AttributeError("ChangeTrigger.change is a write-only property")

    @change.setter
    def change(self, change):
        """ Notify any observers about a change. """

        self.changed.emit(change)

    @property
    def nr_observers(self):
        """ The number of observers of this change. """

        return self._nr_observers

    def remove_observer(self, observer):
        """ Remove an observer of this change. """

        self.changed.disconnect(observer)
        self._nr_observers -= 1


def get_change_trigger(model, name):
    """ Get the change trigger for an attribute of a model.  This is not part
    of the public API.
    """

    return model.__dict__.get('_dip_change_trigger_' + name)
