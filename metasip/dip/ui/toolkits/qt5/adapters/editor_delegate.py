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


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyledItemDelegate

from .....ui import ICollectionEditor, IEditor, EditorFactory

from ..utils import as_QWidget, from_QWidget


class EditorDelegate(QStyledItemDelegate):
    """ The EditorDelegate class is an internal class that acts as a Qt item
    delegate for any editor.
    """

    def __init__(self, editor_factory, attribute_type, parent):
        """ Initialise the delegate.

        :param editor_factory:
            the factory that will create the delegate editor.
        :param attribute_type:
            the type of the value that the editor will be bound to.
        :param parent:
            the parent view.
        """

        super().__init__(parent)

        self._editor_factory = editor_factory
        self._attribute_type = attribute_type

        self.closeEditor.connect(self._editor_closed)

    def createEditor(self, parent, option, index):
        """ Reimplemented to use the editor factory to create the delegated
        editor.
        """

        # We have to be careful with the parent to make sure that an editor
        # implemented as a layout has the right hierachy.
        editor_factory = self._editor_factory
        if isinstance(editor_factory, EditorFactory):
            editor = editor_factory(top_level=False)
        else:
            editor = editor_factory()

        editor = as_QWidget(editor)
        editor.setParent(parent)

        # Prevent the selected value showing through.
        editor.setAutoFillBackground(True)

        return editor

    def setEditorData(self, editor, index):
        """ Reimplemented to set the delegated editor's value using the IEditor
        interface rather than requiring editors to implement a user property.
        """

        data = index.data(Qt.EditRole)
        if data is not None:
            editor = from_QWidget(editor)

            IEditor(editor).value = data

    def setModelData(self, editor, model, index):
        """ Reimplemented to get the delegated editor's value using the IEditor
        interface rather than requiring editors to implement a user property.
        """

        editor = from_QWidget(editor)

        model.setData(index, IEditor(editor).value, Qt.EditRole)

    def _editor_closed(self, editor, hint):
        """ Invoked when a delegated editor is closed. """

        # Note that this implementation means that a delegated editor does not
        # update the invalid reason until the editing is finished, unlike a
        # regular editor which updates the invalid reason as the user types.

        ieditor = IEditor(from_QWidget(editor))

        if ieditor.validator is not None:
            collection_editor = self.parent()
            icollectioneditor = ICollectionEditor(collection_editor)

            invalid_reason = ieditor.validator.validate(ieditor)
            icollectioneditor.save_invalid_reason(invalid_reason)
