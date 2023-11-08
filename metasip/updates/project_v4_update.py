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


from ..dip.model import implements, Model

from ..interfaces import IUpdate


@implements(IUpdate)
class ProjectV4Update(Model):
    """ The ProjectV4Update class implements the update of a project from v3 to
    v4.
    """

    # The project format version number that this will update to (from the
    # immediately previous format).
    updates_to = 4

    def create_view(self, root):
        """ Create the view that will gather the information from the user
        needed to perform the update.

        :param root:
            is the root element of the project.
        :return:
            the view.
        """

        # We don't need any input from the user.
        return None

    def update(self, root, view):
        """ Update a project, including the 'version' attribute.

        :param root:
            is the root element of the project.
        :param view:
            is the view returned by create_view().
        """

        # The v4 schema allows classes to have %ConvertFromTypeCode so we just
        # need to bump the version number.
        root.set('version', str(self.updates_to))
