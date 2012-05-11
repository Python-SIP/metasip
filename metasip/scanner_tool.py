# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from PyQt4.QtGui import QLabel

from dip.model import implements, observe
from dip.shell import IModelSubscriber, SimpleViewTool


@implements(IModelSubscriber)
class ScannerTool(SimpleViewTool):
    """ The ScannerTool implements a tool for handling the scanning of a
    project's header directories.
    """

    # The action's identifier.
    action_id = 'metasip.actions.scanner'

    # The default area for the tool's view.
    area = 'dip.shell.areas.right'

    # The tool's identifier.
    id = 'metasip.tools.scanner'

    # The tool's name.
    name = "Scanner"

    # The collection of actions that the tool's action will be placed in.
    within = 'dip.ui.collections.tools'

    @SimpleViewTool.view.default
    def view(self):
        """ Invoked to create the tool's view. """

        # Create the view.
        return QLabel("No header directories have been defined")

    @observe('published_model')
    def __published_model_changed(self, change):
        """ Invoked when the published model changes. """

        print("Model:", change.new)
