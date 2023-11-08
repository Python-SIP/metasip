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


from .i_automated import IAutomated


class IAutomatedTableEditor(IAutomated):
    """ The IAutomatedTableEditor interface defines the API of automated
    editors that handle tables.
    """

    def simulate_append(self, id, delay, values, editor_is_open=True):
        """ Simulate the user appending a row to the table.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param values:
            is the sequence of values to append.
        :param editor_is_open:
            is set if an editor for the first editable column is already open.
        """

    def simulate_remove(self, id, delay):
        """ Simulate the user removing the currently selected row from the
        table.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        """

    def simulate_select(self, id, delay, row):
        """ Simulate the user selecting a row in the table.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param row:
            is the row to select.
        """

    def simulate_update(self, id, delay, value, row, column):
        """ Simulate the user updating a value in the table.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param value:
            is the new value.
        :param row:
            is the row of the value to update.
        :param column:
            is the column of the value to update.
        """
