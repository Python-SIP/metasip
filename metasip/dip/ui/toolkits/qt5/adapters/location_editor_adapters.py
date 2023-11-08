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


from PyQt5.QtWidgets import QAbstractButton, QLineEdit

from .....model import adapt, Instance, Model

from .editor_adapters import EditorLayoutAdapter, EditorWidgetAdapter


class LocationEditorAdapterMixin(Model):
    """ A mixin for adapters implementing widget and layout based location
    editors.
    """

    # The optional browse button.
    tk_browse_button = Instance(QAbstractButton)

    # The line editor.
    tk_line_edit = Instance(QLineEdit)

    def set_focus(self):
        """ Give the focus to the view. """

        self.tk_line_edit.setFocus()

    def tk_configure(self, layout, properties):
        """ Configure the editor. """

        # For automation purposes give the line edit the id if it doesn't
        # already have one.
        if self.tk_line_edit.objectName() == '':
            self.tk_line_edit.setObjectName(self.id)

        # Apply any properties to the line edit.
        try:
            self.tk_line_edit.pyqtConfigure(**properties)
        except AttributeError:
            pass

    @classmethod
    def tk_isadaptable(cls, layout):
        """ Determine if a layout contains a line editor. """

        if layout is None:
            return False

        line_editor, _ = cls.tk_get_components(layout)

        return line_editor is not None

    def tk_initialise(self, layout):
        """ Initialise the editor. """

        line_edit, browse_button = self.tk_get_components(layout)

        # Connect things up.
        line_edit.textEdited.connect(self.tk_editor_notify)

        if browse_button is not None:
            browse_button.clicked.connect(self.tk_browse)

        self.tk_line_edit = line_edit
        self.tk_browse_button = browse_button

    @staticmethod
    def tk_get_components(layout):
        """ Return a 2-tuple of the line editor and the optional browse button.
        """

        line_editor = browse_button = None

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()

            if isinstance(widget, QLineEdit):
                line_editor = widget
            elif isinstance(widget, QAbstractButton):
                browse_button = widget

        return line_editor, browse_button

    def tk_read_only_getter(self):
        """ Get the read-only state. """

        return self.tk_line_edit.isReadOnly()

    def tk_read_only_setter(self, value):
        """ Set the read-only state. """

        self.tk_line_edit.setReadOnly(value)

        if self.tk_browse_button is not None:
            self.tk_browse_button.setVisible(not value)

    def tk_value_getter(self):
        """ Get the value. """

        return self.tk_line_edit.text()

    def tk_value_setter(self, value):
        """ Set the value. """

        # Save for the notifier.
        self.tk_editor_old_value = value

        self.tk_line_edit.setText(value)


class LocationEditorLayoutAdapter(EditorLayoutAdapter, LocationEditorAdapterMixin):
    """ The LocationEditorLayoutAdapter class is a base class for adapters that
    implement location editors based on a layout containing a line edit and a
    browse button.
    """

    def __init__(self):
        """ Initialise the object. """

        super().__init__()

        self.tk_initialise(self.adaptee)

    def configure(self, properties):
        """ Configure the editor. """

        self.tk_configure(self.adaptee, properties)


class LocationEditorWidgetAdapter(EditorWidgetAdapter, LocationEditorAdapterMixin):
    """ The LocationEditorLayoutAdapter class is a base class for adapters that
    implement location editors based on a widget containing a line edit and a
    browse button.
    """

    def __init__(self):
        """ Initialise the object. """

        super().__init__()

        self.tk_initialise(self.adaptee.layout())

    def configure(self, properties):
        """ Configure the editor. """

        self.tk_configure(self.adaptee.layout(), properties)
