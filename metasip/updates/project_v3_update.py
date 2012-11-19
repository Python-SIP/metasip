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


from xml.etree import ElementTree

from dip.model import implements, Model

from PyQt4.QtGui import QComboBox

from ..interfaces import IUpdate


@implements(IUpdate)
class ProjectV3Update(Model):
    """ The ProjectV2Update class implements the update of a project from v2 to
    v3.
    """

    # The project format version number that this will update to (from the
    # immediately previous format).
    updates_to = 3

    def create_view(self, root):
        """ Create the view that will gather the information from the user
        needed to perform the update.

        :param root:
            is the root element of the project.
        :return:
            the view.
        """

        # We don't need any inout from the user.
        return None

    def update(self, root, view):
        """ Update a project, including the 'version' attribute.

        :param root:
            is the root element of the project.
        :param view:
            is the view returned by create_view().
        """

        # The v3 schema allows enum values to have features and platforms, so
        # we just need to bump the version number.
        root.set('version', str(self.updates_to))
