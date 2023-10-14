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


from dip.model import Bool, Int, Interface, Str


class IUpdate(Interface):
    """ The IUpdate interface is implemented by project updates. """

    # The instruction to the user for completing the view (if there is one).
    instruction = Str()

    # Set if the update is required, ie. the previous version of the project
    # cannot still be supported.
    required_update = Bool(True)

    # The project format version number that this will update to (from the
    # immediately previous format).
    updates_to = Int()

    def create_view(self, root):
        """ Create an optional view that will gather any information from the
        user needed to perform the update.

        :param root:
            is the root element of the project.
        :return:
            the view or ``None`` if no user input is required.
        """

    def update(self, root, view):
        """ Update a project, including the 'version' attribute.

        :param root:
            is the root element of the project.
        :param view:
            is the view returned by create_view().
        """
