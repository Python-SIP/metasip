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


from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtWidgets import QFormLayout

from .....model import Instance, notify_observers, observe
from .....ui import IView

from .object_adapter import ObjectAdapter


class ViewLayoutAdapter(ObjectAdapter):
    """ The ViewLayoutAdapter class is a base class for adapters that implement
    the remainder of the :class:`~dip.pui.IView` interface for Qt layouts.
    """

    def all_views(self):
        """ Create a generator that will return this view and any views
        contained in it.

        :return:
            the generator.
        """

        yield self

    @IView.enabled.setter
    def enabled(self, value):
        """ Invoked to set the enabled state. """

        layout = self.adaptee

        for w in self._tk_view_widgets(layout):
            w.setEnabled(value)

        # If we are a form field then handle any label as well.
        label = self.__tk_view_field_label(layout)
        if label is not None:
            label.setEnabled(value)

    @IView.status_tip.setter
    def status_tip(self, value):
        """ Invoked to set the status tip. """

        for w in self._tk_view_widgets(self.adaptee):
            w.setStatusTip(value)

    @IView.tool_tip.setter
    def tool_tip(self, value):
        """ Invoked to set the tool tip. """

        for w in self._tk_view_widgets(self.adaptee):
            w.setToolTip(value)

    @IView.visible.setter
    def visible(self, value):
        """ Invoked to set the visible state. """

        layout = self.adaptee

        for w in self._tk_view_widgets(layout):
            w.setVisible(value)

        # If we are a form field then handle any label as well.
        label = self.__tk_view_field_label(layout)
        if label is not None:
            label.setVisible(value)

    @IView.whats_this.setter
    def whats_this(self, value):
        """ Invoked to set the "What's This?" help. """

        for w in self._tk_view_widgets(self.adaptee):
            w.setWhatsThis(value)

    def set_focus(self):
        """ Give the focus to the view. """

        views = self.views

        if len(views) > 0:
            views[0].set_focus()

    def tk_view_configure(self, views):
        """ Configure a new set of views. """

        for view in views:
            if not isinstance(view, IView):
                continue

            # Only update the sub-views for non-default values:

            if not self.enabled:
                view.enabled = False

            if view.status_tip == '':
                view.status_tip = self.status_tip

            if view.tool_tip == '':
                view.tool_tip = self.tool_tip

            if not self.visible:
                view.visible = False

            if view.whats_this == '':
                view.whats_this = self.whats_this

    @staticmethod
    def __tk_view_field_label(layout):
        """ Return the label widget if a layout is a form field. """

        parent_layout = layout.parent()

        if isinstance(parent_layout, QFormLayout):
            return parent_layout.labelForField(layout)

        return None

    @classmethod
    def _tk_view_widgets(cls, layout):
        """ A generator that returns the QWidgets within a layout. """

        for idx in range(layout.count()):
            itm = layout.itemAt(idx)

            w = itm.widget()
            if w is not None:
                yield w
            else:
                l = itm.layout()
                if l is not None:
                    yield from cls._tk_view_widgets(l)


class ViewWidgetAdapter(ObjectAdapter):
    """ The ViewWidgetAdapter class is a base class for adapters than implement
    the remainder of the :class:`~dip.pui.IView` interface for Qt widgets.
    """

    # The close event filter.
    _close_event_filter = Instance(QObject)

    # The show event filter.
    _show_event_filter = Instance(QObject)

    def all_views(self):
        """ Create a generator that will return this view and any views
        contained in it.

        :return:
            the generator.
        """

        yield self

    @IView.enabled.getter
    def enabled(self):
        """ Invoked to get the enabled state. """

        return self.adaptee.isEnabled()

    @enabled.setter
    def enabled(self, value):
        """ Invoked to set the enabled state. """

        widget = self.adaptee

        widget.setEnabled(value)

        # If we are a form field then handle any label as well.  Note that the
        # widget's layout may not have been set yet - this is taken care of
        # when the widget becomes visible.
        label = self.__tk_view_field_label(widget)
        if label is not None:
            label.setEnabled(value)

    @IView.status_tip.getter
    def status_tip(self):
        """ Invoked to get the status tip. """

        return self.adaptee.statusTip()

    @status_tip.setter
    def status_tip(self, value):
        """ Invoked to set the status tip. """

        self.adaptee.setStatusTip(value)

    @IView.title.getter
    def title(self):
        """ Invoked to get the title. """

        return self.adaptee.windowTitle()

    @title.setter
    def title(self, value):
        """ Invoked to set the title. """

        self.adaptee.setWindowTitle(value)

    @IView.tool_tip.getter
    def tool_tip(self):
        """ Invoked to get the tool tip. """

        return self.adaptee.toolTip()

    @tool_tip.setter
    def tool_tip(self, value):
        """ Invoked to set the tool tip. """

        self.adaptee.setToolTip(value)

    @IView.visible.getter
    def visible(self):
        """ Invoked to get the visible state. """

        return self.adaptee.isVisible()

    @visible.setter
    def visible(self, value):
        """ Invoked to set the visible state. """

        widget = self.adaptee

        widget.setVisible(value)

        # If we are a form field then handle any label as well.
        label = self.__tk_view_field_label(widget)
        if label is not None:
            label.setVisible(value)

    @IView.whats_this.getter
    def whats_this(self):
        """ Invoked to get the "What's This?" help. """

        return self.adaptee.whatsThis()

    @whats_this.setter
    def whats_this(self, value):
        """ Invoked to set the "What's This?" help. """

        self.adaptee.setWhatsThis(value)

    def set_focus(self):
        """ Give the focus to the view. """

        self.adaptee.setFocus()

    @observe('close_request_handlers')
    def __close_request_handlers_changed(self, change):
        """ Invoked when the list of close request handlers changes. """

        if self._close_event_filter is not None:
            if len(change.new) == 0:
                self.adaptee.removeEventFilter(self._close_event_filter)
                self._close_event_filter = None
        elif len(change.new) != 0:
            self._close_event_filter = CloseEventFilter(self)
            self.adaptee.installEventFilter(self._close_event_filter)

    @IView.ready.observed
    def ready(self, nr_observers):
        """ Invoked when the number of observers changes. """

        if self._show_event_filter is not None:
            if nr_observers == 0:
                self._tk_view_remove_show_event_filter()
        elif nr_observers != 0:
            self._show_event_filter = ShowEventFilter(self)
            self.adaptee.installEventFilter(self._show_event_filter)

    def _tk_view_remove_show_event_filter(self):
        """ Remove the show event filter. """

        self.adaptee.removeEventFilter(self._show_event_filter)
        self._show_event_filter = None

    @classmethod
    def __tk_view_field_label(cls, widget):
        """ Return the label widget if a widget is a form field. """

        if not widget.isWindow():
            parent = widget.parent()
            if parent is not None:
                layout = parent.layout()
                if layout is not None:
                    container = cls.__tk_view_search_layout(layout, widget)
                    if isinstance(container, QFormLayout):
                        return container.labelForField(widget)

        return None

    @classmethod
    def __tk_view_search_layout(cls, layout, widget):
        """ Recursively search a layout for a widget.  Return the layout that
        actually contains the widget.
        """

        for idx in range(layout.count()):
            itm = layout.itemAt(idx)

            w = itm.widget()
            if w is widget:
                return layout

            l = itm.layout()
            if l is not None:
                container = cls.__tk_view_search_layout(l, widget)
                if container is not None:
                    return container

        return None


class CloseEventFilter(QObject):
    """ CloseEventFilter is an internal class that filters a widget's close
    events.
    """

    def __init__(self, widget_adapter):
        """ Initialise the object. """

        super().__init__()

        self._widget_adapter = widget_adapter

    def eventFilter(self, obj, event):
        """ Reimplemented to handle any close events. """

        if event.type() == QEvent.Close:
            view = IView(obj)

            for handler in self._widget_adapter.close_request_handlers:
                if not handler(view):
                    event.ignore()
                    break
            else:
                event.accept()

            return True

        return super().eventFilter(obj, event)


class ShowEventFilter(QObject):
    """ ShowEventFilter is an internal class that filters a widget's show
    events.
    """

    def __init__(self, widget_adapter):
        """ Initialise the object. """

        super().__init__()

        self._widget_adapter = widget_adapter

    def eventFilter(self, obj, event):
        """ Reimplemented to handle any show events. """

        if event.type() == QEvent.Show:
            notify_observers('ready', self._widget_adapter, True, False)

            self._widget_adapter._tk_view_remove_show_event_filter()

        return super().eventFilter(obj, event)
