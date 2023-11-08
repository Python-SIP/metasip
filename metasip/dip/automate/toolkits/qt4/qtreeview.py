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


from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QTreeView
from PyQt4.QtTest import QTest

from ....automate import (AutomationError, IAutomatedEditor,
        IAutomatedListEditor, IAutomatedTableEditor)
from ....model import adapt, Adapter
from ....ui import IListEditor, ITableEditor


class AutomatedCollectionEditorAdapter(Adapter):
    """ The base class for adapters that implement automated collection editors
    based on QTreeView.
    """

    def tk_append(self, id, delay, values):
        """ Simulate the user appending a row to the QTreeView. """

        model = self.adaptee.model()

        nr_values = len(values)

        if nr_values == 0:
            raise AutomationError(id, 'append',
                    "at least one value must be given")

        nr_columns = model.columnCount()

        if nr_values > nr_columns:
            raise AutomationError(id, 'append',
                    "{0} values given for {0} columns".format(nr_values,
                            nr_columns))

        row = model.rowCount() - 1

        editor_is_open = True
        for column in range(nr_values):
            self._tk_update_cell('append', id, delay, row, column,
                    values[column], editor_is_open=editor_is_open)
            editor_is_open = False

    def tk_select(self, id, delay, row):
        """ Simulate the user selecting a row from the QTreeView. """

        qtreeview = self.adaptee
        model = qtreeview.model()

        index = model.indexFromItem(model.item(row, 0))
        qtreeview.scrollTo(index)

        QTest.mouseClick(qtreeview.viewport(), Qt.LeftButton, Qt.NoModifier,
                qtreeview.visualRect(index).center(), delay)

    def tk_update(self, id, delay, value, row, column):
        """ Simulate the user updating a value in the table. """

        self._tk_update_cell('update', id, delay, row, column, value)

    def _tk_update_cell(self, command, id, delay, row, column, value, editor_is_open=False):
        """ Update a cell with a value. """

        qtreeview = self.adaptee
        model = qtreeview.model()

        if row < 0 or row >= model.rowCount():
            raise AutomationError(id, command, "invalid row")

        if column < 0 or column >= model.columnCount():
            raise AutomationError(id, command, "invalid column")

        if not editor_is_open:
            itm = model.item(row, column)
            if itm.flags() & Qt.ItemIsEditable == 0:
                raise AutomationError(id, command,
                        "column {0} is not editable".format(column))

            index = model.indexFromItem(itm)
            qtreeview.setCurrentIndex(index)
            qtreeview.edit(index)

        # Wait for the editor to appear.  We can't assume either that there is
        # one available, or that it might soon appear.
        timeout = 50
        editor = self._tk_editor_widget()
        while editor is None:
            if timeout < 0:
                raise AutomationError(id, command, "no editor widget found")

            QTest.qWait(5)
            timeout -= 5
            editor = self._tk_editor_widget()

        # Update the editor.
        IAutomatedEditor(editor).simulate_set(id, delay, value)

        # Finish editing.
        QTest.keyClick(editor, Qt.Key_Return, Qt.NoModifier, delay)

        # Give Qt a chance to tidy up and update the model.
        QTest.qWait(100)

    def _tk_editor_widget(self):
        """ Return the widget that seems to implement the current editor. """

        # It's a shame that Qt doesn't provide an appropriate call.
        editor = QApplication.focusWidget()

        if editor is None:
            return None

        if editor is self.adaptee:
            return None

        if not self.adaptee.isAncestorOf(editor):
            return None

        return editor


@adapt(QTreeView, to=IAutomatedListEditor)
class QTreeViewIAutomatedListEditorAdapter(AutomatedCollectionEditorAdapter):
    """ An adapter to implement IAutomatedListEditor for a QTreeView. """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QTreeView.

        :param adaptee:
            is the QTreeView.
        :return:
            ``True`` if the QTreeView can be adapted.
        """

        # A QTreeView can be adapted to either IListEditor or ITableEditor.  As
        # we have no control over the order in which these are tried we require
        # that it must already have been adapted to the correct one.  This only
        # really affects non-dip UIs.
        return IListEditor(adaptee, adapt=False) is not None

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

        list_editor = IListEditor(self.adaptee)

        values = []

        for col_nr, col in enumerate(list_editor.columns):
            if col.bind_to != '':
                column_value = getattr(value, col.bind_to)
            else:
                if col_nr != 0:
                    raise AutomationError(id, 'append',
                            "column {0} is not bound to an attribute".format(
                                    col_nr))

                column_value = value

            values.append(column_value)

        # If an editor is already open then we assume that there has been a
        # previous call to IListEditor.append_new_element(open_editor=True),
        # typically by a controller in response to a button press.  Otherwise
        # we do it now.
        if not editor_is_open:
            list_editor.append_new_element(open_editor=True)

        self.tk_append(id, delay, values)

    def simulate_remove(self, id, delay):
        """ Simulate the user removing the currently selected value from the
        list.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        """

        IListEditor(self.adaptee).remove_selected_element()

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

        self.tk_select(id, delay, index)

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

        if column == '':
            col_nr = 0
        else:
            # Convert the attribute name to a column number.
            for col_nr, col in enumerate(IListEditor(self.adaptee).columns):
                if col.bind_to == column:
                    break
            else:
                raise AutomationError(id, 'update',
                        "'{0}' is not bound to a column".format(column))

        self.tk_update(id, delay, value, index, col_nr)


@adapt(QTreeView, to=IAutomatedTableEditor)
class QTreeViewIAutomatedTableEditorAdapter(AutomatedCollectionEditorAdapter):
    """ An adapter to implement IAutomatedTableEditor for a QTreeView. """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QTreeView.

        :param adaptee:
            is the QTreeView.
        :return:
            ``True`` if the QTreeView can be adapted.
        """

        # A QTreeView can be adapted to either IListEditor or ITableEditor.  As
        # we have no control over the order in which these are tried we require
        # that it must already have been adapted to the correct one.  This only
        # really affects non-dip UIs.
        return ITableEditor(adaptee, adapt=False) is not None

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

        # If an editor is already open then we assume that there has been a
        # previous call to ITableEditor.append_new_row(open_editor=True),
        # typically by a controller in response to a button press.  Otherwise
        # we do it now.
        if not editor_is_open:
            ITableEditor(self.adaptee).append_new_row(open_editor=True)

        self.tk_append(id, delay, values)

    def simulate_remove(self, id, delay):
        """ Simulate the user removing the currently selected row from the
        table.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        """

        ITableEditor(self.adaptee).remove_selected_row()

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

        self.tk_select(id, delay, row)

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

        self.tk_update(id, delay, value, row, column)
