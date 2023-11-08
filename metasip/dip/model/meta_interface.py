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


from .adapter import unadapted
from .adapter_internals import adapt_explicitly, object_adapter
from .meta_model import MetaModel


class MetaInterface(MetaModel):
    """ The MetaInterface class is the meta-class for Interface and is
    responsible for making an interface appear to be a super-class and invoking
    adapters when necessary.
    """

    def __call__(cls, obj, adapt=True, cache=True, exception=True, adapter=None):
        """ This is called to create an instance of an object that implements
        an interface, either directly or by adaptation.

        :param obj:
            is the object that may need adapting.
        :param adapt:
            is ``True`` if an adapter is to be created if needed.  If ``False``
            then ``None`` is returned unless the object already implements the
            interface or an appropriate adapter has already been created.
        :param cache:
            is ``True`` if any adapter that is created is cached so that the
            same adapter is returned next time one is needed.
        :param exception:
            is ``True`` if an exception should be raised if an adapter would be
            needed but an appropriate one could not be found.
        :param adapter:
            is the adapter to use.  If it is ``None`` then an appropriate
            adapter is chosed automatically.  If it is not ``None`` then the
            other optional arguments are ignored.
        :return:
            an object, possibly an adapter, that implements the interface.
        """

        # Don't try and adapt an adapter.
        obj = unadapted(obj)

        if adapter is not None:
            adapt_explicitly(obj, cls, adapter)
            return adapter

        # Handle the trivial case where an adapter isn't required.
        if isinstance(obj, cls):
            return obj

        return object_adapter(obj, cls, adapt, cache, exception)

    def __instancecheck__(cls, instance):
        """ Reimplemented to ensure that isinstance() treats an object that
        directly implements an interface as being an instance of that
        interface.  Note that an object that only implements an interface using
        adaptation is not considered an instance.
        """

        subclass = instance.__class__

        for interface in getattr(subclass, '_dip_interfaces', ()):
            if issubclass(interface, cls):
                return True

        # Fall back to the default implementation.
        return super().__instancecheck__(instance)

    def __subclasscheck__(cls, subclass):
        """ Reimplemented to ensure that issubclass() treats a class that
        directly implements an interface as being a sub-class of that
        interface.
        """

        for interface in getattr(subclass, '_dip_interfaces', ()):
            if issubclass(interface, cls):
                return True

        # Fall back to the default implementation.
        return super().__subclasscheck__(subclass)
