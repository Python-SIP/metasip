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


import weakref

from ..model import implements, List, Model

from .i_extension_point import IExtensionPoint


@implements(IExtensionPoint)
class ExtensionPoint(Model):
    """ The ExtensionPoint class is the default implementation of an
    :term:`extension point`.
    """

    # The attributes that are bound to the extension point.
    _bindings = List()

    def bind(self, obj, name):
        """ Bind an attribute of an object to the extension point and update it
        with all contributions made so far.

        :param obj:
            is the object containing the attribute to bind to.
        :param name:
            is the name of the attribute to bind to.
        """

        weak_obj = weakref.ref(obj, self._remove_binding)
        self._bindings.append((weak_obj, name))

        bound = getattr(obj, name)

        for contribution in self.contributions:
            bound.append(contribution)

    def contribute(self, contribution):
        """ Contribute an object to all bound attributes.

        :param contribution:
            is the object to contribute.
        """

        self.contributions.append(contribution)

        for weak_obj, name in self._bindings:
            bound = getattr(weak_obj(), name)
            bound.append(contribution)

    def _remove_binding(self, weak_obj):
        """ Remove an extension point binding when the bound object is
        deleted.
        """

        self._bindings = [
                (wo, name) for wo, name in self._bindings
                        if wo is not weak_obj]
