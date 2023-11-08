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


class IAutomatedListEditor(IAutomated):
    """ The IAutomatedListEditor interface defines the API of automated editors
    that handle lists.
    """

    def simulate_append(self, id, delay, value, editor_is_open=True):
        """ Simulate the user appending a value to the list.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param value:
            is the value to append.  If all the columns are bound to attributes
            then the value is assumed to be an instance of a model.  Otherwise
            there must only be a single column and the value must be a single
            value.
        :param editor_is_open:
            is set if an editor for the first editable column is already open.
        """

    def simulate_remove(self, id, delay):
        """ Simulate the user removing the currently selected value from the
        list.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        """

    def simulate_select(self, id, delay, index):
        """ Simulate the user selecting a value in the list.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param index:
            is the index of the value to select.
        """

    def simulate_update(self, id, delay, value, index, column=''):
        """ Simulate the user updating a value in the list.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param value:
            is the new value.
        :param index:
            is the index of the value to update.
        :param column:
            is the name of the attribute within the model to update.  It should
            not be specified if the list's elements are a simple type.
        """
