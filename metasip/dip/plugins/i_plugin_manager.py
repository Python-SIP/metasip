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


from ..model import Interface, List

from .i_extension_point import IExtensionPoint
from .i_plugin import IPlugin
from .i_service import IService


class IPluginManager(Interface):
    """ The IPluginManager interface defines the API of a
    :term:`plugin manager`.
    """

    # The list of extension points.
    extension_points = List(IExtensionPoint)

    # The list of contributed plugins.
    plugins = List(IPlugin)

    # The list of contributed services.
    services = List(IService)

    def bind_extension_point(self, id, obj, name):
        """ Bind an extension point to an attribute of an object.  The
        attribute must have an ``append()`` method.

        :param id:
            is the identifier of the extension point.
        :param obj:
            is the object containing the attribute that the extension point is
            bound to.
        :param name:
            is the name of the attribute that the extension point is bound to.
        """

    def bind_service(self, interface, obj, name):
        """ Bind the service for an interface to an attribute of an object.

        :param interface:
            is the interface.
        :param obj:
            is the object containing the attribute that the service is bound
            to.
        :param name:
            is the name of the attribute that the service is bound to.
        """

    def contribute(self, id, contribution):
        """ Contribute an object to an extension point.

        :param id:
            is the identifier of the extension point.
        :param contribution:
            is the contribution to make to the extension point.
        """

    def service(self, interface):
        """ Get a service for a particular interface.

        :param interface:
            is the interface.
        :return:
            the service which will implement or be able to be adapted to the
            interface.  An exception is raised if there is no service
            available.
        """

    def choose_service(self, services):
        """ Choose a particular service from a list of possible services.

        :param services:
            a list of contributed services to choose from.
        :return:
            the chosen service or ``None`` if one wasn't chosen.
        """
