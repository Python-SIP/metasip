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


from dip.model import implements, observe
from dip.publish import ISubscriber
from dip.shell import SimpleViewTool
from dip.ui import IViewBinding

from ...interfaces.project import IProject


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
                GroupBox, HBox, Label, LineEditor, MessageArea, PushButton,
                Splitter, Stretch, VBox, ViewStack)

        from .module_validator import ModuleValidator
        from .scanner_controller import ScannerController
        from .scanner_model import ScannerModel

        # The view factory.
        view_factory = ViewStack(
                VBox(
                    Label('no_project_text'),
                    Stretch(),
                    id='metasip.scanner.no_project'),
                Splitter(
                    ViewStack(id='metasip.scanner.project_views'),
                    VBox(
                        Form(
                            ComboBox('working_version'),
                            FilesystemLocationEditor('source_directory',
                                    id='metasip.scanner.source_directory',
                                    mode='directory'),
                            id='metasip.scanner.scan_form'),
                        GroupBox(
                            VBox(
                                Form(
                                    Label('header_directory_name',
                                            label="Name"),
                                    'suffix',
                                    'file_filter',
                                    'parser_arguments'),
                                Grid(
                                    PushButton('scan'),
                                    PushButton('update_directory',
                                            label="Update"),
                                    PushButton('hide_ignored'),
                                    PushButton('show_ignored'),
                                    nr_columns=2)),
                            title="Header Directory",
                            id='metasip.scanner.directory_group'),
                        GroupBox(
                            VBox(
                                Form(
                                    Label('header_file_name', label="Name"),
                                    LineEditor('module',
                                            validator=ModuleValidator()),
                                    'ignored'),
                                HBox(
                                    PushButton('parse'),
                                    PushButton('update_file',
                                            label="Update"))),
                            title="Header File",
                            id='metasip.scanner.file_group'),
                        HBox(
                            PushButton('new', label="New..."),
                            PushButton('delete', enabled=False),
                            PushButton('reset_workflow', enabled=False)),
                        Stretch(),
                        MessageArea()),
                    id='metasip.scanner.splitter'),
                controller_factory=ScannerController)

        # Create the view.
        return view_factory(ScannerModel(), top_level=False)

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        event = change.new.event
        project = change.new.model
        controller = IViewBinding(self.view).controller

        if event == 'dip.events.opened':
            controller.open_project(project)
        elif event == 'dip.events.closed':
            controller.close_project(project)
        elif event == 'dip.events.active':
            controller.activate_project(project)
