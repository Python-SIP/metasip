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


from .....model import Adapter
from .....ui import IObject


class ObjectAdapter(Adapter):
    """ The ObjectAdapter class is a base class for adapters than implement the
    :class:`~dip.ui.IObject` interface.
    """

    @IObject.id.getter
    def id(self):
        """ Invoked to get the id. """

        return self.adaptee.objectName()
    
    @id.setter
    def id(self, value):
        """ Invoked to set the id. """
        
        self.adaptee.setObjectName(value)
        
    def configure(self, properties):
        """ Configure the object using a mapping of toolkit specific property
        names and values.

        :param properties:
            is the mapping of the properties.
        """

        obj = self.adaptee

        blocked = obj.blockSignals(True)

        try:
            obj.pyqtConfigure(**properties)
        except AttributeError:
            pass

        obj.blockSignals(blocked)
