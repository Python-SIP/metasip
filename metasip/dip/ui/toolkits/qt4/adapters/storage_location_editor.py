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


from PyQt4.QtGui import QBoxLayout, QWidget

from .....io import IFilterHints, IoManager, IIoManagerUi, IStorageLocation
from .....model import adapt, DelegatedTo, Instance
from .....ui import IStorageLocationEditor

from .location_editor_adapters import (LocationEditorLayoutAdapter,
		LocationEditorWidgetAdapter)


class StorageLocationEditorAdapterMixin:
    """ A mixin for adapters to implementing IStorageocationEditor for widgets
    and layouts.
    """

    # The filter hints.
    filter = DelegatedTo('filter_hints')

    # Remember the storage location between clicks of the browse button.
    _tk_default_location = Instance(IStorageLocation)

    @IStorageLocationEditor.read_only.getter
    def read_only(self):
        """ Invoked to get the read-only state. """

        return self.tk_read_only_getter()

    @read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only state. """

        self.tk_read_only_setter(value)

    @IStorageLocationEditor.value.getter
    def value(self):
        """ Invoked to get the editor's value. """

        return self.tk_value_getter()

    @value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        self.tk_value_setter(value)

    def tk_browse(self):
        """ Invoked when the browse button is clicked. """

        line_edit = self.tk_line_edit
        browse_button = self.tk_browse_button

        iiomanagerui = IIoManagerUi(IoManager.ui)

        if self.mode == 'open':
            location = iiomanagerui.readable_storage_location(
                    self.title if self.title != '' else "Open",
                    default_location=self._tk_default_location,
                    format=self.format, hints=self, parent=browse_button)
        else:
            location = iiomanagerui.writeable_storage_location(
                    self.title if self.title != '' else "Save",
                    default_location=self._tk_default_location,
                    format=self.format, hints=self, parent=browse_button)

        line_edit.activateWindow()
        line_edit.setFocus()

        if location is not None:
            self._tk_default_location = location
            self.value = str(location)


@adapt(QBoxLayout, to=[IStorageLocationEditor, IFilterHints])
class QBoxLayoutIStorageLocationEditorLayoutAdapter(LocationEditorLayoutAdapter, StorageLocationEditorAdapterMixin):
    """ An adapter to implement IStorageLocationEditor for a QBoxLayout. """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QBoxLayout.

        :param adaptee:
            is the QWidget.
        :return:
            ``True`` if the QBoxLayout can be adapted.
        """

        return cls.tk_isadaptable(adaptee)


@adapt(QWidget, to=[IStorageLocationEditor, IFilterHints])
class QWidgetIStorageLocationEditorWidgetAdapter(LocationEditorWidgetAdapter, StorageLocationEditorAdapterMixin):
    """ An adapter to implement IStorageLocationEditor for a QWidget. """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QWidget.

        :param adaptee:
            is the QWidget.
        :return:
            ``True`` if the QWidget can be adapted.
        """

        return cls.tk_isadaptable(adaptee.layout())
