#!/usr/bin/env python3

# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.io import IoManager, IStorage, StorageError, IStorageLocation


# FIXME: Shouldn't IFilterHints be part of ICodec?


def io_IoManager_read(model, format, location):
    """ Read a model from a location using a particular format.

    :param model:
        is the model.
    :param format:
        is the format.
    :param location:
        is the location as a string.  This should identify a valid and
        unambiguous storage location.
    :return:
        the read model.  This may be the original model populated from the
        storage location, or it may be a different model (of an appropriate
        type) created from the storage location.
    """

    locations = IoManager.readable_locations_from_string(format, location)

    if len(locations) != 1:
        raise StorageError("unknown or ambiguous location", location)

    location = locations[0]

    return IStorage(IStorageLocation(location).storage).read(model, location)


def io_IoManager_write(model, format, location):
    """ Write a model to a location using a particular format.

    :param model:
        is the model.
    :param format:
        is the format.
    :param location:
        is the location as a string.  This should identify a valid and
        unambiguous storage location.
    """

    locations = IoManager.writeable_locations_from_string(format, location)

    if len(locations) != 1:
        raise StorageError("unknown or ambiguous location", location)

    location = locations[0]

    IStorage(IStorageLocation(location).storage).write(model, location)
