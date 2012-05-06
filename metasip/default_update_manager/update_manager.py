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
from dip.ui import Application

from ..interfaces import IUpdate, IUpdateManager


@implements(IUpdateManager)
class UpdateManager(Model):
    """ The UpdateManager class is the default implementation of the project
    update manager.
    """

    def update(self, root, update_to):
        """ Update a project to a later format.

        :param root:
            is the root element of the project.
        :param update_to:
            is the project version to update to.
        :return:
            True if the update was done or False if the user cancelled.
        """

        # Check that we know how to do the requested updates.
        update_from = int(root.get('version'))

        iupdates = []
        for format in range(update_from + 1, update_to + 1):
            for update in self.updates:
                iupdate = IUpdate(update)

                if iupdate.updates_to == format:
                    iupdates.append(iupdate)
                    break
            else:
                Application.warning("Updating Project",
                        "The project has format v{0} and needs to be updated "
                        "to v{1} but there is no update from v{2} to "
                        "v{3}.".format(update_from, update_to, format - 1,
                                format))

                return False

        # Do the updates.
        for iupdate in iupdates:
            iupdate.update(root)

        return True
