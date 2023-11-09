# Copyright (c) 2023 Riverbank Computing Limited.
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


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QAbstractItemView, QApplication, QTreeView

from .....model import adapt, Bool, Instance, Int, Model, notify_observers
from .....ui import IListEditor, ITableEditor

from .editor_delegate import EditorDelegate
from .view_adapters import ViewWidgetAdapter


class CollectionEditorAdapter(ViewWidgetAdapter):
    """ The base class for adapters that implement collection editors based on
    QTreeView.
    """

    # The tree views's model.
    tk_q_model = Instance(QStandardItemModel)

    # Set if the model is being updated.  (We don't block the signals in case
    # that causes problems with the view.)
    _tk_updating_q_model = Bool()

    def configure(self, properties):
        """ Configure the editor. """

        tree_view = self.adaptee

        tree_view.setRootIsDecorated(False)
        tree_view.setModel(self.tk_q_model)
        tree_view.selectionModel().selectionChanged.connect(
                self.__on_selection_changed)

        # If read_only has the default value then it may not have been
        # explicitly set.
        if not self.read_only:
            self.tk_set_read_only(False)

        super().configure(properties)

    def remove_title(self):
        """ Remove an editor's title.  This will only be called if the title
        policy is 'optional'.  This implementation does nothing.
        """

    def retrieve_invalid_reason(self):
        """ Retrieve the invalid reason for an item in the collection.

        :return:
            is the invalid reason.  It will be an empty string if all items are
            valid.
        """

        tree_view = self.adaptee
        model = self.tk_q_model

        # Find an invalid item giving preference to the current cell.
        itm = model.itemFromIndex(tree_view.currentIndex())

        reason = '' if itm is None else itm.data(Qt.ItemDataRole.UserRole)
        if reason == '':
            for row_nr in range(model.rowCount()):
                for col_nr in range(model.columnCount()):
                    itm = model.item(row_nr, col_nr)
                    if itm is None:
                        continue

                    reason = itm.data(Qt.ItemDataRole.UserRole)
                    if reason != '':
                        break

        if reason != '':
            row_nr = itm.row()

            if len(self.columns) == 1:
                reason = "in row {0}, {2}".format(row_nr + 1, reason)
            else:
                col_nr = itm.column()

                col_itm = model.horizontalHeaderItem(col_nr)
                if col_itm is None:
                    col_name = "column {0}".format(col_nr)
                else:
                    col_name = col_itm.text()

                reason = "in row {0} of '{1}', {2}".format(row_nr + 1,
                        col_name, reason)

        return reason

    def save_invalid_reason(self, invalid_reason):
        """ Save the invalid reason for the current item in the collection.

        :param invalid_reason:
            is the invalid reason.  It will be an empty string if the item is
            valid.
        """

        tree_view = self.adaptee
        model = self.tk_q_model

        model.itemFromIndex(tree_view.currentIndex()).setData(
                Qt.ItemDataRole.UserRole, invalid_reason)

    @tk_q_model.default
    def tk_q_model(self):
        """ Invoked to return the default model. """

        model = QStandardItemModel(self.adaptee)

        model.itemChanged.connect(self.__on_item_changed)

        return model

    def tk_edit_last_row(self):
        """ Open the editor for the first editable column in the last row. """

        tree_view = self.adaptee
        model = self.tk_q_model

        row_nr = model.rowCount() - 1

        for col_nr in range(model.columnCount()):
            itm = model.item(row_nr, col_nr)
            if itm.flags() & Qt.ItemFlag.ItemIsEditable:
                index = model.indexFromItem(itm)

                tree_view.setCurrentIndex(index)
                tree_view.edit(index)

                break

    def tk_get_cell(self, row, col, col_nr):
        """ Get the value of a cell. """

        raise NotImplementedError

    def tk_new_element(self, item_values):
        """ Convert a list of item values to an appropriate list element. """

        raise NotImplementedError

    def tk_set_columns(self, value):
        """ Invoked to set the columns. """

        tree_view = self.adaptee
        model = self.tk_q_model

        # Set the number of columns.
        model.clear()
        model.setColumnCount(len(value))

        # Configure the headings.
        headings = []
        has_headings = False

        for col_nr, col in enumerate(value):
            tree_view.setItemDelegateForColumn(col_nr,
                    EditorDelegate(col.editor_factory, col.column_type,
                            self.adaptee))

            headings.append(col.heading if col.heading else '')
            if col.heading is not None:
                has_headings = True

        if has_headings:
            model.setHorizontalHeaderLabels(headings)
            tree_view.setHeaderHidden(False)
        else:
            tree_view.setHeaderHidden(True)

    def tk_set_read_only(self, value):
        """ Invoked to set the read-only state. """

        model = self.tk_q_model

        # Change the editable state of every item in the model.
        for row_nr in range(model.rowCount()):
            for col_nr, col in enumerate(self.columns):
                itm = model.item(row_nr, col_nr)
                flags = itm.flags()

                if value:
                    flags &= ~Qt.ItemFlag.ItemIsEditable
                elif col.editable:
                    flags |= Qt.ItemFlag.ItemIsEditable

                itm.setFlags(flags)

        if value:
            self.adaptee.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            self.adaptee.setEditTriggers(QAbstractItemView.DoubleClicked |
                    QAbstractItemView.EditKeyPressed |
                    QAbstractItemView.SelectedClicked)

    def tk_set_selectable(self, value):
        """ Set if the editor is selectable. """

        tree_view = self.adaptee

        if value:
            mode = QAbstractItemView.SingleSelection
        else:
            mode = QAbstractItemView.NoSelection

            selection_model = tree_view.selectionModel()
            blocked = selection_model.blockSignals(True)
            selection_model.clear()
            selection_model.blockSignals(blocked)

        tree_view.setSelectionMode(mode)

    def tk_get_selection(self, selection_range):
        """ Return the selection from a selection range. """

        raise NotImplementedError

    def tk_set_value(self, value):
        """ Invoked to set the editor's value. """

        model = self.tk_q_model

        model.removeRows(0, model.rowCount())

        for row_nr, row_value in enumerate(value):
            self.tk_new_row(row_nr, row_value)

    def tk_new_row(self, row_nr, row_value):
        """ Create a new row of items. """

        model = self.tk_q_model

        self._tk_updating_q_model = True

        for col_nr, col in enumerate(self.columns):
            itm = QStandardItem()

            if not self.read_only and col.editable:
                itm.setFlags(itm.flags() | Qt.ItemFlag.ItemIsEditable)

            itm.setData(self.tk_get_cell(row_value, col, col_nr),
                    Qt.ItemDataRole.EditRole)
            itm.setData('', Qt.ItemDataRole.UserRole)

            model.setItem(row_nr, col_nr, itm)

        self._tk_updating_q_model = False

    def tk_start_value_change(self):
        """ Return a closure to be passed to tk_complete_value_change(). """

        # The clsure is a shallow copy of the actual value.
        return list(self._value)

    def tk_complete_value_change(self, closure):
        """ Complete the change of the value. """

        notify_observers('value', self, self._value, closure)

    def __on_item_changed(self, itm):
        """ Invoked when the user has changed an item in the model. """

        if self._tk_updating_q_model:
            return

        model = self.tk_q_model

        # Start the change to the value.
        closure = self.tk_start_value_change()

        del self._value[:]

        for row_nr in range(model.rowCount()):
            item_values = [model.item(row_nr, col_nr).data(Qt.ItemDataRole.EditRole)
                    for col_nr in range(model.columnCount())]

            self._value.append(self.tk_new_element(item_values))

        # Complete the change to the value.
        self.tk_complete_value_change(closure)

    def __on_selection_changed(self, selected, deselected):
        """ Invoked when the selection changes. """

        self._selection = self.tk_get_selection(selected)
        old_selection = self.tk_get_selection(deselected)

        if self._selection != old_selection:
            notify_observers('selection', self, self._selection, old_selection)


@adapt(QTreeView, to=IListEditor)
class QTreeViewIListEditorAdapter(CollectionEditorAdapter):
    """ An adapter to implement IListEditor for a QTreeView. """

    @IListEditor.columns.setter
    def columns(self, value):
        """ Invoked to set the columns. """

        self.tk_set_columns(value)

    @IListEditor.title_policy.getter
    def title_policy(self):
        """ Invoked to get the title policy. """

        return 'default' if self.columns[0].bind_to != '' else 'embedded'

    @IListEditor.read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only state. """

        self.tk_set_read_only(value)

    @IListEditor.selectable.setter
    def selectable(self, value):
        """ Invoked to set if elements can be selected. """

        self.tk_set_selectable(value)

    @IListEditor.selection.setter
    def selection(self, value):
        """ Invoked to set the index of the selection. """

        if self.selectable:
            selection_model = self.adaptee.selectionModel()

            if value < 0:
                selection_model.clear()
            else:
                model = self.tk_q_model

                selection_model.select(model.indexFromItem(model.item(value)),
                        QItemSelectionModel.Select | QItemSelectionModel.Rows)

    @IListEditor.value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        self.tk_set_value(value)

    def append_new_element(self, open_editor=True):
        """ A new element, created by calling the element factory, is appended
        to the list.
        """

        element = self.element_factory()

        closure = self.tk_start_value_change()

        self.tk_new_row(self.tk_q_model.rowCount(), element)
        self._value.append(element)

        self.tk_complete_value_change(closure)

        if open_editor:
            self.tk_edit_last_row()

    def remove_selected_element(self):
        """ The currently selected element is removed. """

        idx = self.selection

        if idx < 0:
            raise ValueError("there is no selected element")

        closure = self.tk_start_value_change()

        self.tk_q_model.removeRow(idx)
        del self._value[idx]

        self.tk_complete_value_change(closure)

    def tk_get_cell(self, row, col, col_nr):
        """ Get the value of a cell. """

        if col.bind_to != '':
            return getattr(row, col.bind_to)

        # The view factory will ensure there is only one column in this case.
        return row

    def tk_new_element(self, item_values):
        """ Convert a list of item values to an appropriate list element. """

        if self.columns[0].bind_to == '':
            element = item_values[0]
            if element is None:
                element = self.element_factory()
        else:
            element = self.element_factory()

            for col_nr, col in enumerate(self.columns):
                cell_value = item_values[col_nr]
                if cell_value is not None:
                    setattr(element, col.bind_to, cell_value)
            
        return element

    def tk_get_selection(self, selection_range):
        """ Return the selection from a selection range. """

        indexes = selection_range.indexes()

        if len(indexes) == 0:
            return -1

        return self.tk_q_model.itemFromIndex(indexes[0]).row()


@adapt(QTreeView, to=ITableEditor)
class QTreeViewITableEditorAdapter(CollectionEditorAdapter):
    """ An adapter to implement ITableEditor for a QTreeView. """

    @ITableEditor.columns.setter
    def columns(self, value):
        """ Invoked to set the columns. """

        self.tk_set_columns(value)

    @ITableEditor.read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only state. """

        self.tk_set_read_only(value)

    @ITableEditor.selection.setter
    def selection(self, value):
        """ Invoked to set the index of the selection. """

        mode = self.selection_mode

        if mode != 'none':
            selection_model = self.adaptee.selectionModel()

            if mode == 'row':
                row_nr = value
                col_nr = 0
                select = QItemSelectionModel.Rows
            elif mode == 'column':
                row_nr = 0
                col_nr = value
                select = QItemSelectionModel.Columns
            else:
                row_nr, col_nr = value
                select = 0

            if row_nr < 0 or col_nr < 0:
                selection_model.clear()
            else:
                model = self.tk_q_model
                index = model.indexFromItem(model.item(row_nr, col_nr))

                selection_model.select(index,
                        QItemSelectionModel.Select | select)

    @ITableEditor.selection_mode.setter
    def selection_mode(self, value):
        """ Invoked to set set if elements can be selected. """

        if value == 'none':
            self.tk_set_selectable(False)
        else:
            if value == 'item':
                select = QAbstractItemView.SelectItems
            elif value == 'column':
                select = QAbstractItemView.SelectColumns
            else:
                select = QAbstractItemView.SelectRows

            self.adaptee.setSelectionBehavior(select)
            self.tk_set_selectable(True)

    @ITableEditor.value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        self.tk_set_value(value)

    def append_new_row(self, open_editor=True):
        """ A new row, created by calling the row factory, is appended to the
        list.
        """

        row = self.row_factory()

        closure = self.tk_start_value_change()

        self.tk_new_row(self.tk_q_model.rowCount(), row)
        self._value.append(row)

        self.tk_complete_value_change(closure)

        if open_editor:
            self.tk_edit_last_row()

    def remove_selected_row(self):
        """ The currently selected row is removed. """

        if self.selection_mode == 'row':
            idx = self.selection

            if idx < 0:
                raise ValueError("there is no selected row")

            closure = self.tk_start_value_change()

            self.tk_q_model.removeRow(idx)
            del self._value[idx]

            self.tk_complete_value_change(closure)

    def tk_get_cell(self, row, col, col_nr):
        """ Get the value of a cell. """

        return row[col_nr]

    def tk_new_element(self, item_values):
        """ Convert a list of item values to an appropriate list element. """

        element = []

        for col_nr, value in enumerate(item_values):
            if value is None:
                value = self.row_factory()[col_nr]

            element.append(value)

        return element

    def tk_get_selection(self, selection_range):
        """ Return the selection from a selection range. """

        indexes = selection_range.indexes()

        if len(indexes) == 0:
            itm = None
        else:
            itm = self.tk_q_model.itemFromIndex(indexes[0])

        mode = self.selection_mode

        if mode == 'row':
            return -1 if itm is None else itm.row()

        if mode == 'column':
            return -1 if itm is None else itm.column()

        return (-1, -1) if itm is None else (itm.row(), itm.column())
