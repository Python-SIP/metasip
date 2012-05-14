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


from dip.model import implements, List, Model, observe, Str, Trigger
from dip.publish import ISubscriber
from dip.shell import SimpleViewTool

from .interfaces.project import IProject


@implements(ISubscriber)
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

    # The type of models we subscribe to.
    subscription_type = IProject

    # The collection of actions that the tool's action will be placed in.
    within = 'dip.ui.collections.tools'

    @SimpleViewTool.view.default
    def view(self):
        """ Invoked to create the tool's view. """

        from dip.ui import (ComboBox, FilesystemLocationEditor, Form, Grid,
                GroupBox, Label, PushButton, Splitter, Stretch, VBox,
                ViewStack)

        # The view factory.
        view_factory = ViewStack(
                VBox(
                    Label('no_project_text'),
                    Stretch()),
                Splitter(
                    ViewStack(),
                    VBox(
                        Form(
                            ComboBox('working_version', options='versions',
                                    visible=False),
                            FilesystemLocationEditor('source_directory')),
                        GroupBox(
                            VBox(
                                Form('header_directory_suffix', 'file_filter',
                                        'parser_arguments'),
                                'update'),
                                title="Properties"),
                        Grid(
                            PushButton('scan', enabled=False),
                            PushButton('restart', label="Restart Workflow"),
                            PushButton('new', label="New..."),
                            PushButton('delete', enabled=False),
                            nr_columns=2),
                        Stretch())))

        # Create the view.
        return view_factory(ScannerModel())

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        print(change.new.model, "is", change.new.event)


class ScannerModel(Model):

    delete = Trigger()

    no_project_text = Str("There is no project to scan.")

    file_filter = Str()

    header_directory_suffix = Str()

    new = Trigger()

    parser_arguments = Str()

    restart = Trigger()

    scan = Trigger()

    source_directory = Str()

    update = Trigger()

    versions = List(Str())

    working_version = Str(None, allow_none=True)
