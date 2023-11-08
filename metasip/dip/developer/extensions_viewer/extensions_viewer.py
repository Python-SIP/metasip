# Copyright (c) 2017 Riverbank Computing Limited.
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


import functools

# FIXME: replace with proper toolkit support.
from ... import TOOLKIT
if TOOLKIT == 'qt4':
    from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem
else:
    from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from ...model import observe
from ...plugins import PluginManager
from ...ui import IDisplay


class ExtensionsViewer(QTreeWidget):
    """ The ExtensionsViewer class is a widget that implements a read-only
    visualisation of all extension points.
    """

    def __init__(self):
        """ Initialise the viewer. """

        super().__init__()

        self.setHeaderLabels(["Identifier", "Contribution"])

        pluginmanager = PluginManager().instance
        self._new_extension_points(pluginmanager.extension_points)
        observe('extension_points', pluginmanager,
                self.__extension_points_changed)

    def __extension_points_changed(self, change):
        """ Invoked when the list of extension points changes. """

        # At the moment extension points can only be added.
        self._new_extension_points(change.new)

    def _new_extension_points(self, extension_points):
        """ Add a list of new extension points. """

        for extension_point in extension_points:
            itm = QTreeWidgetItem(self, [extension_point.id, ''])

            # Add any existing contributions.
            for contribution in extension_point.contributions:
                self._add_contribution(itm, contribution)

            observe('contributions', extension_point,
                    functools.partial(self.__new_contribution, itm))

    def __new_contribution(self, parent, change):
        """ Invoked when a new contribution is made to an extension point. """

        # At the moment contributions can only be added.
        for contribution in change.new:
            self._add_contribution(parent, contribution)

    @staticmethod
    def _add_contribution(parent, contribution):
        """ Add a new contribution. """

        id = getattr(contribution, 'id', '')

        tool_tip = str(contribution)

        idisplay = IDisplay(contribution, exception=False)
        name = '' if idisplay is None else idisplay.name
        if name == '':
            name = tool_tip

        itm = QTreeWidgetItem(parent, [id, name])
        itm.setToolTip(1, tool_tip)
