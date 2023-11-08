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


from .....model import notify_observers
from .....ui import IEditor

from .view_adapters import ViewLayoutAdapter, ViewWidgetAdapter


class EditorAdapterMixin:
    """ A mixin for adapters implementing IEditor for widgets and layouts. """

    def tk_editor_notify(self, new):
        """ Notify any observers about a change in value. """

        old = self.tk_editor_old_value

        if new != old:
            self.tk_editor_old_value = new
            notify_observers('value', self, new, old)


class EditorLayoutAdapter(ViewLayoutAdapter, EditorAdapterMixin):
    """ The EditorLayoutAdapter class is a base class for adapters than
    implement the :class:`~dip.pui.IEditor` interface for Qt layouts.
    """

    def remove_title(self):
        """ Remove an editor's title.  This will only be called if the title
        policy is 'optional'.  This default implementation does nothing.
        """

    @IEditor.read_only.getter
    def read_only(self):
        """ Invoked to get the read-only state. """

        # It is read-only if every top-level QWidget within the layout is
        # read-only.
        is_ro = self._read_only

        for w in self._tk_view_widgets(self.adaptee):
            if hasattr(w, 'isReadOnly'):
                if not w.isReadOnly():
                    return False

                is_ro = True

        return is_ro

    @read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only state. """

        for w in self._tk_view_widgets(self.adaptee):
            if hasattr(w, 'setReadOnly'):
                w.setReadOnly(value)


class EditorWidgetAdapter(ViewWidgetAdapter, EditorAdapterMixin):
    """ The EditorWidgetAdapter class is a base class for adapters than
    implement the :class:`~dip.pui.IEditor` interface for Qt widgets.
    """

    def remove_title(self):
        """ Remove an editor's title.  This will only be called if the title
        policy is 'optional'.  This default implementation does nothing.
        """
