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


import types

from .delegated_to import DelegatedTo
from .observe import observe
from .trigger import Trigger
from .type_factory import TypeFactory
from .value_type_factory import Uninitialized, ValueTypeFactory


# Handle specific toolkits differently so that models can be used as mixins.
# FIXME: replace with proper toolkit support.
from .. import TOOLKIT
if TOOLKIT == 'qt4':
    from PyQt4.QtCore import QObject
else:
    from PyQt5.QtCore import QObject


class MetaModel(type(QObject)):
    """ The MetaModel class is the meta-class for Model and is responsible for
    initialising the attributes of an instance.
    """

    def __new__(meta_cls, name, bases, cls_dict):
        """ Reimplemented to create the type cache. """

        # Create the class as normal.
        cls = super().__new__(meta_cls, name, bases, cls_dict)

        type_cache = {}

        # Go through the MRO in reverse order so that local attributes replace
        # more distant ones automatically.
        for mro in reversed(cls.__mro__):
            for aname, atype in mro.__dict__.items():
                if isinstance(atype, TypeFactory):
                    # The descriptor needs to know the attribute name.  If it
                    # already has a name then it has been bound elsewhere and
                    # we need a clone.
                    if atype.name is not None:
                        atype = atype.clone()
                        setattr(mro, aname, atype)
                    else:
                        # Remember the defining type.
                        atype.model_type = mro

                    atype.name = aname

                    # Cache the completed type.
                    type_cache[aname] = atype
                    continue

                # See if this is a decorated observer.
                if type(atype) is types.FunctionType:
                    observed = getattr(atype, '_dip_observed', None)
                    if observed is not None:
                        type_cache[aname] = observed
                        continue

                # See if this is overriding the default value of an attribute.
                orig_atype = type_cache.get(aname)
                if isinstance(orig_atype, ValueTypeFactory):
                    # Create a clone of the original type but with the new
                    # default.
                    new_atype = orig_atype.clone()
                    new_atype.set_default_value(atype)

                    # The default decorator takes precedence except when a
                    # sub-class declares the attribute as a simple value.
                    new_atype._default_func = None

                    # Replace the value with the new type and update the type
                    # cache.
                    setattr(mro, aname, new_atype)
                    type_cache[aname] = new_atype

        setattr(cls, '_dip_type_cache', type_cache)

        return cls

    def __call__(cls, *args, **kwargs):
        """ This is called to create an instance of a class we are a meta-class
        of.
        """

        # Create the instance as normal.
        instance = cls.__new__(cls)

        # Get the type cache.
        type_cache = getattr(cls, '_dip_type_cache')

        # Handle any keyword arguments that correspond to types.
        init_kwargs = kwargs.copy()
        delegates = []
        observers = []
        cache_items = type_cache.items()

        # This first pass is for everything except setting explicit initial
        # values, i.e. anything that won't invoke a custom setter.
        for aname, atype in cache_items:
            # Setup any decorated observer.
            if isinstance(atype, list):
                observer = getattr(instance, aname)

                for oname in atype:
                    observers.append((oname, instance, observer))

                continue

            # Get the type's value if given, otherwise get it later when it is
            # first referenced.
            value = init_kwargs.get(aname, Uninitialized)

            if isinstance(atype, DelegatedTo):
                if value is not Uninitialized:
                    # Remember the initialisation of any delegates.
                    delegates.append((aname, value))
            elif isinstance(atype, ValueTypeFactory):
                shadow = '_' + aname

                if value is Uninitialized:
                    # Set the default if there is no default function.
                    if atype._default_func is None:
                        value = atype.get_default_value()
                        atype.bind(instance, value)
                else:
                    value = atype.get_default_value()

                setattr(instance, shadow, value)

        # Now set any explicit initial values.  This is done separately from
        # the above so that custom setters can rely on other attributes having
        # their correct initial values.
        for aname, atype in cache_items:
            value = init_kwargs.pop(aname, Uninitialized)
            if value is Uninitialized:
                continue

            if isinstance(atype, ValueTypeFactory):
                # Save the explicit initial value.
                atype.set_value(instance, aname, value)

        # We can now initialise any delegates now that the other (possibly
        # dependent) attributes have been set up.
        for aname, value in delegates:
            setattr(instance, aname, value)

        # Now set up the observers.
        for aname, instance, observer in observers:
            observe(aname, instance, observer)

        # Initialise the instance with the modified keyword arguments.
        instance.__class__.__init__(instance, *args, **init_kwargs)

        return instance
