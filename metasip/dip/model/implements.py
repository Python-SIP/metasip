# Copyright (c) 2009 Riverbank Computing Limited.
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


from .inject import inject
from .model import Model


def implements(*interfaces):
    """ A class decorator that marks the class as implementing one or more
    interfaces.  If a class implements an interface then :func:`issubclass`
    will return ``True`` when tested against the interface, :func:`isinstance`
    will return ``True`` when an instance of the class is tested against the
    interface.  The decorator will automatically add any attributes of an
    interface that are not already present in the class.

    :param interfaces:
        are the interfaces that the class implements.
    """

    def decorator(cls):
        """ The decorator function. """

        if not issubclass(cls, Model):
            raise TypeError("implements() must decorate a sub-class of Model")

        inject(cls, interfaces)

        return cls

    return decorator
