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


from ..model import Callable, Instance, Interface, List

from .i_codec import ICodec
from .i_io_manager_ui import IIoManagerUi
from .i_storage_factory import IStorageFactory


class IIoManager(Interface):
    """ The IIoManager interface defines the API of an i/o manager. """

    # The available codecs.
    codecs = List(ICodec)

    # The available storage factories.
    storage_factories = List(IStorageFactory)

    # The storage policies that determines if a format is allowed to be written
    # to or read from storage represented by a particular implementation of
    # :class:`~dip.io.IStorage`.  Each policy is called with the format
    # identifier and the storage as arguments.  A policy should return ``True``
    # if the access is allowed.  All policies must return ``True`` for the
    # access to proceed.
    storage_policies = List(Callable())

    # The storage-independent user interfaces.
    ui = Instance(IIoManagerUi)

    def read(self, model, location, format):
        """ Read a model from a location using a particular format.

        :param model:
            is the model.
        :param location:
            is the location as a string.  This should identify a valid and
            unambiguous storage location.
        :param format:
            is the format.
        :return:
            the read model.  This may be the original model populated from the
            storage location, or it may be a different model (of an appropriate
            type) created from the storage location.  If ``None`` is returned
            then it is assumed that the read was abandoned and the user
            informed appropriately.
        """

    def readable_locations_from_string(self, location, format=''):
        """ Get the list of readable storage location instances for which a
        location specified as a string is valid.

        :param location:
            is the location as a string.
        :param format:
            is the identifier of the optional format.
        :return:
            the list of storage location instances.
        """

    def readable_storage(self, format=''):
        """ Get the list of the storage instances that can be read from using a
        particular format.

        :param format:
            is the identifier of the optional format.
        :return:
            the list of storage instances.
        """

    def write(self, model, location, format):
        """ Write a model to a location using a particular format.

        :param model:
            is the model.
        :param location:
            is the location as a string.  This should identify a valid and
            unambiguous storage location.
        :param format:
            is the format.
        """

    def writeable_locations_from_string(self, location, format=''):
        """ Get the list of writeable storage location instances for which a
        location specified as a string is valid.

        :param location:
            is the location as a string.
        :param format:
            is the identifier of the optional format.
        :return:
            the list of storage location instances.
        """

    def writeable_storage(self, format=''):
        """ Get the list of the storage instances that can be written to using
        a particular format.

        :param format:
            is the identifier of the optional format.
        :return:
            the list of storage instances.
        """
