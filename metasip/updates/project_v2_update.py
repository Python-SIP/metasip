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


from dip.model import implements, Model

from ..interfaces import IUpdate


@implements(IUpdate)
class ProjectV2Update(Model):
    """ The ProjectV2Update class implements the update of a project from v1 to
    v2.
    """

    # The project format version number that this will update to (from the
    # immediately previous format).
    updates_to = 2

    def update(self, root):
        """ Update a project, including the 'version' attribute.

        :param root:
            is the root element of the project.
        """

        print("Updating to v2")

        root.set('version', str(self.updates_to))
