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


from ..dip.model import Interface, List

from .i_update import IUpdate


class IUpdateManager(Interface):
    """ The IUpdateManager interface is implemented by project update managers.
    """

    # The list of available updates.
    updates = List(IUpdate)

    def update_is_required(self, root):
        """ See if a project needs to be updated.

        :param root:
            is the root element of the project.
        :return:
            True if any update to the current version is required.
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
