# Copyright (c) 2011 Riverbank Computing Limited.
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


from .any import Any
from .model import Model


class Adapter(Model):
    """ The Adapter class is the base class for all :term:`adapters<adapter>`.
    """

    # The object that is being adapted.  It will be set automatically when the
    # adapter is created.
    adaptee = Any()

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a particular object.  It is
        only called after it is known that the adapter can handle the object's
        type.

        :param adaptee:
            is the object to be adapted.
        :return:
            ``True`` if the object can be adapted.  This default implementation
            always returns ``True``.
        """

        return True


def unadapted(obj):
    """ Return an unadapted object from what might be an adapter.
    
    :param obj:
        is the object, which may be an adapter.
    :return:
        the unadapted object.
    """

    return obj.adaptee if isinstance(obj, Adapter) else obj
