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


from PyQt6.QtCore import QItemSelectionModel, Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QAbstractItemView, QListView

from .....model import adapt, Bool, Instance
from .....ui import IDisplay, IOptionList

from .editor_adapters import EditorWidgetAdapter


@adapt(QListView, to=IOptionList)
class QListViewIOptionListAdapter(EditorWidgetAdapter):
    """ An adapter to implement IOptionList for a QListView. """

    # The list views's model.
    _tk_model = Instance(QStandardItemModel)

    # Set if the adapter is updating the model (rather than the user).
    _tk_updating_model = Bool(False)

    def configure(self, properties):
        """ Configure the editor. """

        list_view = self.adaptee

        # If read_only has the default value then it may not have been
        # explicitly set.
        if not self.read_only:
            self._set_read_write()

        list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        list_view.setModel(self._tk_model)

        list_view.selectionModel().selectionChanged.connect(
				self._on_selection_changed)

        super().configure(properties)

    @IOptionList.labels.setter
    def labels(self, value):
        """ Invoked to set the labels. """

        model = self._tk_model

        self._tk_updating_model = True

        # For each item see if we have a new label allowing for the items
        # having been sorted.
        nr_labels = len(value)

        for row in range(model.rowCount()):
            itm = model.item(row)
            option = itm.data(Qt.UserRole)

            idx = self.options.index(option)

            if idx < nr_labels:
                label = value[idx]
            else:
                label = self._option_as_str(option)

            itm.setText(label)

        if self.sorted:
            model.sort(0)

        self._tk_updating_model = False

    @IOptionList.options.setter
    def options(self, value):
        """ Invoked to set the options. """

        list_view = self.adaptee
        model = self._tk_model

        self._tk_updating_model = True

        # Set the number of rows and columns.
        model.clear()
        model.setRowCount(len(value))
        model.setColumnCount(1)

        # Set the options before sorting.
        for idx, option in enumerate(value):
            try:
                as_str = self.labels[idx]
            except IndexError:
                as_str = self._option_as_str(option)

            itm = QStandardItem(as_str)
            itm.setData(option, Qt.UserRole)

            model.setItem(idx, 0, itm)

        if self.sorted:
            model.sort(0)

        self._tk_updating_model = False

    @IOptionList.sorted.setter
    def sorted(self, value):
        """ Invoked to set the sorted state. """

        if value:
            self._tk_model.sort(0)

    @IOptionList.value.getter
    def value(self):
        """ Invoked to get the editor's value. """

        return self._get_value()

    @value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        # Save for the notifier.
        self.tk_editor_old_value = value

        self._tk_updating_model = True
        self._set_value(value)
        self._tk_updating_model = False

    @IOptionList.read_only.getter
    def read_only(self):
        """ Invoked to get the read-only state. """

        return self.adaptee.selectionMode() == QAbstractItemView.NoSelection

    @read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only state. """

        if value:
            self.adaptee.setSelectionMode(QAbstractItemView.NoSelection)
        else:
            self._set_read_write()

    @_tk_model.default
    def _tk_model(self):
        """ Invoked to return the default model. """

        return QStandardItemModel(self.adaptee)

    @staticmethod
    def _option_as_str(option):
        """ Return the string representation of an option. """

        idisplay = IDisplay(option, exception=False)
        as_str = '' if idisplay is None else idisplay.name

        return as_str if as_str != '' else str(option)

    def _set_read_write(self):
        """ Configure the view so that it can be edited. """

        self.adaptee.setSelectionMode(QAbstractItemView.SingleSelection)

    def _on_selection_changed(self, selected, deselected):
        """ Invoked when the selection changes. """

        if not self._tk_updating_model:
            self.tk_editor_notify(self._get_value())

    def _get_value(self):
        """ Get the editor's value. """

        itm = self._tk_model.itemFromIndex(
                self.adaptee.selectionModel().currentIndex())

        return None if itm is None else itm.data(Qt.UserRole)

    def _set_value(self, value):
        """ Set the editor's value. """

        list_view = self.adaptee
        model = list_view.model()

        if value is None:
            itm = None
        else:
            for row_nr in range(model.rowCount()):
                itm = model.item(row_nr)

                if itm.data(Qt.UserRole) == value:
                    break
            else:
                raise ValueError("'{0}' is not a valid option".format(value))

        if itm is None:
            list_view.selectionModel().clear()
        else:
            list_view.setCurrentIndex(model.indexFromItem(itm))
