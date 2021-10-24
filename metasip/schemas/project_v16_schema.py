# Copyright (c) 2021 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.io import IFilterHints
from dip.model import implements, Model
from dip.ui import IDisplay

from ..interfaces import ISchema


@implements(ISchema, IDisplay, IFilterHints)
class ProjectV16Schema(Model):
    """ The ProjectV16Schema class validates an XML file against the project
    v16 schema.
    """

    # The filter.
    filter = "MetaSIP project v16 files (*.msp)"

    # The name to be displayed to the user.
    name = "MetaSIP project v16"

    # The name of the schema file relative to this file.
    schema_file = 'project_v16.xsd'
