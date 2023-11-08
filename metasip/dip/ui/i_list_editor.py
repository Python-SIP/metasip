# Copyright (c) 2018 Riverbank Computing Limited.
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


from ..model import Bool, Callable, Int, List

from .i_collection_editor import ICollectionEditor
from .list_column import ListColumn


class IListEditor(ICollectionEditor):
    """ The IListEditor interface defines the API to be implemented by a list
    editor.
    """

    # The list of columns.  There will only be more than one column if elements
    # are model instances.
    columns = List(ListColumn)

    # When called this will create the data for a new element of the list.
    element_factory = Callable()

    # This is set if the list elements are selectable.
    selectable = Bool(True)

    # This is the index of the selected element (or -1 if there is no
    # selection).
    selection = Int()

    # The value of the editor.
    value = List()

    def append_new_element(self, open_editor=True):
        """ A new element, created by calling the element factory, is appended
        to the list.

        :param open_editor:
            If this is ``True`` then an editor will be automatically opened for
            the first editable column of the new element.
        """

    def remove_selected_element(self):
        """ The currently selected element is removed. """
