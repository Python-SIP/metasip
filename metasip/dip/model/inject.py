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


import types

from .interface import Interface
from .model_utils import get_model_types
from .type_factory import TypeFactory


def inject(cls, interfaces):
    """ An internal function that adds any missing interface attributes to a
    class.
    """

    # Update the interfaces the class implements for the meta-type to use in
    # __instancecheck__ and __subclasscheck__.  First see if already implements
    # an interface.
    all_interfaces = cls.__dict__.get('_dip_interfaces')
    if all_interfaces is None:
        # See if any super-classes implement any interfaces.
        all_interfaces = getattr(cls, '_dip_interfaces', None)
        if all_interfaces is None:
            all_interfaces = []
        else:
            # Take a copy of the the super-class's interfaces because we may be
            # updating it.
            all_interfaces = list(all_interfaces)

        setattr(cls, '_dip_interfaces', all_interfaces)

    type_cache = cls.__dict__['_dip_type_cache']

    for interface in interfaces:
        if interface in all_interfaces:
            continue

        if not issubclass(interface, Interface):
            raise TypeError("'{0}' must be a sub-class of Interface".format(
                    type(interface).__name__))

        all_interfaces.append(interface)

        # Add any interface attributes that haven't been explicitly
        # implemented.
        for attr, value in get_model_types(interface).items():
            # Check that the receiving class doesn't already have the
            # attribute.
            if attr not in type_cache:
                try:
                    # See if the receiving class has a new default value.
                    v = cls.__dict__[attr]
                except KeyError:
                    # It doesn't so just inject from the interface.
                    setattr(cls, attr, value)
                    type_cache[attr] = value
                else:
                    # It's not so assume it is the new default value.
                    value = value.clone()
                    value.set_default_value(v)

                    setattr(cls, attr, value)
                    type_cache[attr] = value

        # Check that there are implementations of all interface methods.
        for attr_name in dir(interface):
            try:
                attr = getattr(interface, attr_name)
            except AttributeError:
                # Triggers cannot be read.
                continue

            if isinstance(attr, types.FunctionType):
                missing = True
                try:
                    cls_attr = getattr(cls, attr_name)
                except AttributeError:
                    pass
                else:
                    if isinstance(cls_attr, types.FunctionType):
                        missing = False

                if missing:
                    raise AttributeError(
                            "'{0}' must provide an implementation of "
                            "{1}.{2}()".format(cls.__name__,
                                    interface.__name__, attr_name))
