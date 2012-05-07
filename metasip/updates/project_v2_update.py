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

from PyQt4.QtGui import QComboBox

from ..interfaces import IUpdate


@implements(IUpdate)
class ProjectV2Update(Model):
    """ The ProjectV2Update class implements the update of a project from v1 to
    v2.
    """

    # The instruction to the user.
    instruction = "Select the version that was current when the project's header directories were last scanned. Normally this would be the latest version.\n"

    # The project format version number that this will update to (from the
    # immediately previous format).
    updates_to = 2

    def create_view(self, root):
        """ Create the view that will gather the information from the user
        needed to perform the update.

        :param root:
            is the root element of the project.
        :return:
            the view.
        """

        versions = root.get('versions', '').split()
        if len(versions) == 0:
            return None

        versions.reverse()

        view = QComboBox()
        view.addItems(versions)

        return view

    def update(self, root, view):
        """ Update a project, including the 'version' attribute.

        :param root:
            is the root element of the project.
        :param view:
            is the view returned by create_view().
        """

        print("Updating to v2:", version)
        if view is not None:
            version = view.currentText()

        del root.attrib['outputdir']

        root.set('version', str(self.updates_to))
