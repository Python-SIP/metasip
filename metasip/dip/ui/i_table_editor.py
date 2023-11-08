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


from ..model import Callable, Enum, Instance, List

from .i_collection_editor import ICollectionEditor
from .table_column import TableColumn


class ITableEditor(ICollectionEditor):
    """ The ITableEditor interface defines the API to be implemented by a table
    editor.
    """

    # The list of columns.
    columns = List(TableColumn)

    # When called this will create the data for a new row in the table.
    row_factory = Callable()

    # This is the index of the current selection.  Whether it is an integer row
    # or column number, or a 2-tuple of row and column numbers depends on the
    # selection mode.  Negative values indicate no selection.
    selection = Instance(int, tuple)

    # The selection mode.
    selection_mode = Enum('row', 'column', 'item', 'none')

    # The value of the editor.
    value = List()

    def append_new_row(self, open_editor=True):
        """ A new row, created by calling the row factory, is appended to the
        list.

        :param open_editor:
            If this is ``True`` then an editor will be automatically opened for
            the first editable column of the new row.
        """

    def remove_selected_row(self):
        """ The currently selected row is removed. """
