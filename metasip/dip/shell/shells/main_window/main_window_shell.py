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


from ....model import Instance
from ....ui import MainWindow, Menu, MenuBar, Stack

from ... import BaseShellFactory


class MainWindowShell(BaseShellFactory):
    """ The MainWindowShell class is a factory for shells that are implemented
    as a toolkit specific main window.
    """

    # The main window factory.
    main_window = Instance(MainWindow)

    def create_shell(self, model, parent, top_level):
        """ Create the view that implements the shell.

        :param model:
            is the model.
        :param parent:
            is the optional parent view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the shell.
        """

        return self.main_window(model, parent, top_level)

    @main_window.default
    def main_window(self):
        """ Get the default main window factory. """

        return MainWindow(Stack(tab_bar='multiple'),
                menu_bar=MenuBar(
                        Menu(
                                'dip.ui.actions.new',
                                'dip.ui.actions.open',
                                'dip.ui.actions.save',
                                'dip.ui.actions.save_as',
                                'dip.ui.actions.close',
                                '',
                                'dip.ui.actions.import',
                                'dip.ui.actions.export',
                                '',
                                'dip.ui.collections.print',
                                '',
                                'dip.ui.actions.quit',
                                title="&File",
                                id='dip.ui.collections.file'),
                        Menu(
                                'dip.ui.collections.undo',
                                title="&Edit",
                                id='dip.ui.collections.edit'),
                        Menu(
                                title="&View",
                                id='dip.ui.collections.view'),
                        Menu(
                                title="&Tools",
                                id='dip.ui.collections.tools'),
                        Menu(
                                'dip.ui.actions.whats_this',
                                title="&Help",
                                id='dip.ui.collections.help')))
