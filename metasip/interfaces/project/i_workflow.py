# Copyright (c) 2020 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.model import Enum, Interface


class IWorkflow(Interface):
    """ The IWorkflow interface is implemented by API items that are subject to
    a workflow.
    """

    # The workflow status of the API item.
    status = Enum('', 'ignored', 'removed', 'todo', 'unknown',
            default='unknown')
