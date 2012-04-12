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


from .i_project import IProject

from .logger import Logger
from .Project import Project
from .project_factory import ProjectFactory
from .project_codec import ProjectCodec

from .dip_future import io_IoManager_read, io_IoManager_write

# Make sure the adapters get registered.
from . import project_adapters
