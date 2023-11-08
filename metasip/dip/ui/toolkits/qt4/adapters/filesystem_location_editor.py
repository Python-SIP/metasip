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


from PyQt4.QtGui import QBoxLayout, QFileDialog, QWidget

from .....model import adapt
from .....ui import IFilesystemLocationEditor

from .location_editor_adapters import (LocationEditorLayoutAdapter,
        LocationEditorWidgetAdapter)


class FilesystemLocationEditorAdapterMixin:
    """ A mixin for adapters to implementing IFilesystemLocationEditor for
    widgets and layouts.
    """

    @IFilesystemLocationEditor.read_only.getter
    def read_only(self):
        """ Invoked to get the read-only state. """

        return self.tk_read_only_getter()

    @read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only state. """

        self.tk_read_only_setter(value)

    @IFilesystemLocationEditor.value.getter
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

        value = self.value
        mode = self.mode
        filter = self.filter

        if mode == 'open_file':
            value, _ = QFileDialog.getOpenFileName(line_edit, directory=value,
                    filter=filter)

        elif mode == 'save_file':
            value, _ = QFileDialog.getSaveFileName(line_edit, directory=value,
                    filter=filter)

        elif mode == 'directory':
            value, _ = QFileDialog.getExistingDirectory(line_edit,
                    directory=value)

        line_edit.activateWindow()
        line_edit.setFocus()

        if value != '':
            self.value = value


@adapt(QBoxLayout, to=IFilesystemLocationEditor)
class QBoxLayoutIFilesystemLocationEditorLayoutAdapter(LocationEditorLayoutAdapter, FilesystemLocationEditorAdapterMixin):
    """ An adapter to implement IFilesystemLocationEditor for a QBoxLayout. """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QBoxLayout.

        :param adaptee:
            is the QWidget.
        :return:
            ``True`` if the QBoxLayout can be adapted.
        """

        return cls.tk_isadaptable(adaptee)


@adapt(QWidget, to=IFilesystemLocationEditor)
class QWidgetIFilesystemLocationEditorWidgetAdapter(LocationEditorWidgetAdapter, FilesystemLocationEditorAdapterMixin):
    """ An adapter to implement IFilesystemLocationEditor for a QWidget. """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QWidget.

        :param adaptee:
            is the QWidget.
        :return:
            ``True`` if the QWidget can be adapted.
        """

        return cls.tk_isadaptable(adaptee.layout())
