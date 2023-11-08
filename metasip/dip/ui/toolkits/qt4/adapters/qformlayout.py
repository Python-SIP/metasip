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


from PyQt4.QtCore import QEvent, QObject
from PyQt4.QtGui import QFormLayout, QWidget

from .....model import adapt, Instance, Model, unadapted
from .....ui import IForm, IView

from .container_adapters import ContainerLayoutAdapter, ContainerWidgetAdapter


class FormAdapterMixin(Model):
    """ A mixin for adapters implementing IForm for widgets and layouts. """

    # The field visibility event filter.
    _tk_visibility_event_filter = Instance(QObject)

    def tk_form_views_getter(self, layout):
        """ Invoked to get a layout's views. """

        views = []
        for row in range(layout.rowCount()):
            itm = layout.itemAt(row, QFormLayout.FieldRole)
            if itm is None:
                itm = layout.itemAt(row, QFormLayout.SpanningRole)
                if itm is None:
                    continue

            w = itm.widget()
            if w is not None:
                views.append(IView(w))
            else:
                l = itm.layout()
                if l is not None:
                    views.append(IView(l))

        return tuple(views)

    def tk_form_views_setter(self, layout, value):
        """ Invoked to set a layout's views. """

        # Clear the layout.
        while layout.count() > 0:
            layout.takeAt(0)

        # Populate the layout.
        for row, field in enumerate(value):
            tk_field = unadapted(field)

            try:
                label = self.labels[row]
            except IndexError:
                label = None

            if label is None:
                layout.addRow(tk_field)
            else:
                layout.addRow(label, tk_field)

                # Set the label's enabled and visible states to match the
                # field's.  Note that Qt won't actually create a label widget
                # if the label is an empty string.
                label_w = layout.labelForField(tk_field)
                if label_w is not None:
                    label_w.setEnabled(field.enabled)
                    label_w.setVisible(field.visible)

                    if isinstance(tk_field, QWidget):
                        # Install an event filter for the field to monitor its
                        # visibility.
                        tk_field.installEventFilter(
                                self._tk_visibility_event_filter)

    @_tk_visibility_event_filter.default
    def _tk_visibility_event_filter(self):
        """ Invoked to return the default field visibility event filter. """

        return VisibilityEventFilter(
                self.adaptee.layout() if isinstance(self.adaptee, QWidget)
                else self.adaptee)


class VisibilityEventFilter(QObject):
    """ VisibilityEventFilter is an internal class that monitors the visibility
    of field widgets.
    """

    def eventFilter(self, obj, event):
        """ Reimplemented to handle any hide and show events. """

        event_type = event.type()

        if event_type == QEvent.Hide:
            self.parent().labelForField(obj).setVisible(False)
        elif event_type == QEvent.Show:
            label = self.parent().labelForField(obj)
            # FIXME: This doesn't seem to come into effect until the window is
            #        activated.
            label.setVisible(True)

            # We also make sure the label's enabled state is up to date.  We
            # can't rely on the setter in the widget adapter because the field
            # widget's layout manager may not have been set at that time.  We
            # also can't rely on the field's state because it may have been set
            # by Qt (e.g. in response to changing the state of a parent), so we
            # use the shadow attribute which reflects the programmer's intent.
            label.setEnabled(IView(obj)._enabled)

        return super().eventFilter(obj, event)


@adapt(QFormLayout, to=IForm)
class QFormLayoutIFormAdapter(ContainerLayoutAdapter, FormAdapterMixin):
    """ An adapter to implement IForm for a QFormLayout. """

    @IForm.views.getter
    def views(self):
        """ Invoked to get the view's sub-views. """

        return self.tk_form_views_getter(self.adaptee)

    @views.setter
    def views(self, value):
        """ Invoked to set the view's sub-views. """

        self.tk_form_views_setter(self.adaptee, value)
        self.tk_view_configure(value)


@adapt(QWidget, to=IForm)
class QWidgetIFormAdapter(ContainerWidgetAdapter, FormAdapterMixin):
    """ An adapter to implement IForm for a QWidget that wraps a QFormLayout.
    """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QWidget.

        :param adaptee:
            is the QWidget.
        :return:
            ``True`` if the QWidget can be adapted.
        """

        return isinstance(adaptee.layout(), QFormLayout)

    @IForm.views.getter
    def views(self):
        """ Invoked to get the view's sub-views. """

        return self.tk_form_views_getter(self.adaptee.layout())

    @views.setter
    def views(self, value):
        """ Invoked to set the view's sub-views. """

        self.tk_form_views_setter(self.adaptee.layout(), value)
