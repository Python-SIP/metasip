# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dataclasses import dataclass

from .annos import Annos
from .tagged import Tagged
from .workflow import Workflow


@dataclass
class Code(Annos, Tagged, Workflow):
    """ This class implements APIs that can be annotated, are subject to
    version control and a workflow.
    """

    # The containing API item (ie. a .sip file or a C/C++ scope).  Note that
    # this isn't part of the project file itself.
    # TODO: is it actually used anymore?  It used to be used to find the
    # project - specifically the ignorednamespaces attribute.
    container: '.code_container.CodeContainer' = None
