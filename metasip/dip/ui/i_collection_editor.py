# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of dip.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from .i_editor import IEditor


class ICollectionEditor(IEditor):
    """ The ICollectionEditor interface defines the API to be implemented
    (typically using adaptation) by an editor that handles a collection type
    (e.g. a list).
    """

    def retrieve_invalid_reason(self):
        """ Retrieve the invalid reason for an item in the collection.

        :return:
            is the invalid reason.  It will be an empty string if all items are
            valid.
        """

    def save_invalid_reason(self, invalid_reason):
        """ Save the invalid reason for the current item in the collection.

        :param invalid_reason:
            is the invalid reason.  It will be an empty string if the item is
            valid.
        """
