# Copyright (c) 2010 Riverbank Computing Limited.
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


from .adapter import Adapter
from .adapter_internals import add_adapter_factory
from .inject import inject


def adapt(*adapted, to):
    """ A class decorator that marks one or more classes, which must be
    sub-classes of :class:`~dip.model.Adapter`, as being able to
    :term:`adapt<adapter>` an object to one or more
    :term:`interfaces<interface>`.  An instance of the adapter will be
    automatically created when required.  Like the
    :func:`~dip.model.implements` class decorator any attributes of the
    interfaces that are not already present in the adapter are automatically
    added.

    :param adapted:
        is the list of types of object to be adapted.
    :param to:
        is the interface (or list of interfaces) that the object is adapted to.
    """

    # Check we are adapting types.
    for a in adapted:
        if not isinstance(a, type):
            raise TypeError("adapt() adapts a type not '{0}'".format(
                    type(a).__name__))

    # Make sure we have a list of interfaces.
    if not isinstance(to, list):
        to = [to]

    def decorator(cls):
        """ The decorator function. """

        if not issubclass(cls, Adapter):
            raise TypeError("adapt() must decorate a sub-class of Adapter")

        # Do an implicit @implements.
        inject(cls, to)

        # Register the adapter as a factory for each interface.
        for interface in to:
            for a in adapted:
                add_adapter_factory(cls, a, interface)

        return cls

    return decorator
