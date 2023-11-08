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


""" The :mod:`dip.io` module implements the infrastructure for defining and
interfacing with :term:`storage`.

Plugins must provide appropriate support for the following extension points:

``dip.io.codecs``
    This must be supported by any plugin that configures an object implementing
    the :class:`dip.io.IIoManager` interface.  A contribution must implement
    the :class:`dip.io.ICodec` interface.

``dip.io.storage_factories``
    This must be supported by any plugin that configures an object implementing
    the :class:`dip.io.IIoManager` interface.  A contribution must implement
    the :class:`dip.io.IStorageFactory` interface.

``dip.io.storage_policies``
    This must be supported by any plugin that configures an object implementing
    the :class:`dip.io.IIoManager` interface.  A contribution must be a
    callable.
"""


from .i_codec import ICodec
from .i_filter_hints import IFilterHints
from .i_io_manager import IIoManager
from .i_io_manager_ui import IIoManagerUi
from .i_storage import IStorage
from .i_storage_browser import IStorageBrowser
from .i_storage_factory import IStorageFactory
from .i_storage_location import IStorageLocation
from .i_storage_ui import IStorageUi
from .i_streaming_storage_factory import IStreamingStorageFactory
from .i_structured_storage_factory import IStructuredStorageFactory

from .base_storage import BaseStorage
from .exceptions import FormatError, StorageError
from .io_manager import IoManager

# Make sure adapters get registered.
from . import istoragelocation_idisplay_adapter
