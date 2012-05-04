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


from dip.model import Instance, List, Str

from .i_annos import IAnnos
from .i_version_range import IVersionRange
from .i_workflow import IWorkflow


class ICode(IAnnos, IVersionRange, IWorkflow):
    """ The ICode interface is implemented by API items that can be annotated,
    are subject to version control and a workflow.
    """

    # The containing API item.
    container = Instance('.ICodeContainer')

    # The optional list of features that the API item is limited to.  A feature
    # may be preceded by "!" to indicate the logical inverse.
    features = List(Str())

    # The optional list of platforms that the API item is limited to.
    platforms = List(Str())
