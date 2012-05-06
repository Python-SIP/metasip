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


from dip.model import Int, Interface


class IUpdate(Interface):
    """ The IUpdate interface is implemented by project updates. """

    # The project format version number that this will update to (from the
    # immediately previous format).
    updates_to = Int()

    def update(self, root):
        """ Update a project, including the 'version' attribute.

        :param root:
            is the root element of the project.
        """
