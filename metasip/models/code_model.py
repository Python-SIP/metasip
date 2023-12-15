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


from ..dip.model import Instance

from .annos_mixin import AnnosMixin
from .tagged_mixin import TaggedMixin
from .workflow_mixin import WorkflowMixin


class CodeModel(AnnosMixin, TaggedMixin, WorkflowMixin):
    """ This class implements APIs that can be annotated, are subject to
    version control and a workflow.
    """

    # The containing API item.
    container = Instance('.CodeContainerMixin')
