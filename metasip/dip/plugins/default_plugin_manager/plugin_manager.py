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


from ...model import implements, Model, observe

from .. import ExtensionPoint, IPluginManager


@implements(IPluginManager)
class PluginManager(Model):
    """ The PluginManager class is the default implementation of the
    :class:`~dip.plugins.IPluginManager` interface.
    """

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

        self._get_extension_point(id).bind(obj, name)

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

        setattr(obj, name, self.service(interface))

    def contribute(self, id, contribution):
        """ Contribute an object to an extension point.

        :param id:
            is the identifier of the extension point.
        :param contribution:
            is the contribution to make to the extension point.
        """

        self._get_extension_point(id).contribute(contribution)

    def service(self, interface):
        """ Get a service for a particular interface.

        :param interface:
            is the interface.
        :return:
            the service which will implement or be able to be adapted to the
            interface.  An exception is raised if there is no service
            available.
        """

        # Get the list of services for this interface.
        services = [service for service in self.services
                if service.interface is interface]

        service = self.choose_service(services)

        if service is None:
            raise TypeError(
                    "there is no service available for '{0}'"
                            .format(interface.__name__))

        return interface(service.implementation)

    def choose_service(self, services):
        """ Choose a particular service from a list of possible services.

        :param services:
            a list of contributed services to choose from.
        :return:
            the chosen service or ``None`` if one wasn't chosen.
        """

        return services[0] if len(services) > 0 else None

    def _get_extension_point(self, id):
        """ Get the extension point for a given identifier, creating it if
        necessary.  Allowing extension points to be defined implicitly allows
        consumers of contributions to be enabled later and still have access
        to all contributions.
        """

        for extension_point in self.extension_points:
            if extension_point.id == id:
                break
        else:
            extension_point = ExtensionPoint(id=id)
            self.extension_points.append(extension_point)

        return extension_point

    @observe('plugins')
    def __plugins_changed(self, change):
        """ Invoked when the list of plugins changes. """

        # FIXME: Handle plugins being removed.

        for plugin in change.new:
            if plugin.enabled:
                self._configure_plugin(plugin)

            observe('enabled', plugin, self.__plugin_enabled_changed)

    def __plugin_enabled_changed(self, change):
        """ Invoked when the enabled state of a plugin changes. """

        # FIXME: Handle disabled.

        if change.new:
            self._configure_plugin(change.model)

    def _configure_plugin(self, plugin):
        """ Configure a plugin. """

        # Check any prerequisites.
        for required in plugin.requires:
            for ip in self.plugins:
                if ip.id == required and ip.enabled:
                    break
            else:
                raise ValueError("plugin '{0}' requires an enabled plugin "
                        "'{1}'".format(plugin.id, required))

        plugin.configure(self)
