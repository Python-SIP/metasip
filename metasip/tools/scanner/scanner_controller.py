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


from dip.model import Instance, observe
from dip.ui import Controller, IEditor, IOptionSelector, IView, IViewStack

from ...interfaces.project import IProject

from .scanner_view import ScannerView


class ScannerController(Controller):
    """ The ScannerController implements the controller for the scanner tool
    GUI.
    """

    # The current project.
    current_project = Instance(IProject)

    # The current project specific user interface.
    current_project_ui = Instance(IView)

    def activate_project(self, project):
        """ Activate a project. """

        self.current_project = project
        self.current_project_ui = project_ui = self._find_view(project)

        # Make sure the project's view is current.
        IViewStack(self.project_views_view).current_view = project_ui

        # Configure the versions.
        self._update_versions()

        # Configure the source directory.
        self.model.source_directory = project_ui.source_directory

    def close_project(self, project):
        """ Close a project. """

        project_views = IViewStack(self.project_views_view).views

        # Remove the observers.
        observe('versions', project, self.__on_versions_changed, remove=True)

        # Remove the project specific part of the GUI.
        del project_views[self._find_view(project)]

        # Hide the GUI if there are no more projects.
        if len(project_views) == 0:
            IViewStack(self.view).current_view = self.no_project_view

    def open_project(self, project):
        """ Open a project. """

        project_views = IViewStack(self.project_views_view).views

        # Show the GUI if it was previously hidden.
        if len(project_views) == 0:
            IViewStack(self.view).current_view = self.splitter_view

        # Create the project specific part of the GUI.
        view = ScannerView(project)
        IViewStack(self.project_views_view).views.append(view)

        # Observe any changes to the versions.
        observe('versions', project, self.__on_versions_changed)

    def validate(self):
        """ Reimplemented to update the state of the view after a change. """

        # This is called very early.
        if self.current_project_ui is None:
            return

        super().validate()

        # Scan is enabled if there is a valid source directory.
        ieditor = IEditor(self.source_directory_editor)
        self.current_project_ui.source_directory = ieditor.value
        IView(self.scan_editor).enabled = (ieditor.invalid_reason == '')

    def _find_view(self, project):
        """ Find the project specific part of the GUI for a project. """

        for view in IViewStack(self.project_views_view).views:
            if view.project == project:
                return view

        # This should never happen.
        return None

    @observe('model.delete')
    def __on_delete_triggered(self, change):
        """ Invoked when the Delete button is triggered. """

        print("Doing Delete")

    @observe('model.new')
    def __on_new_triggered(self, change):
        """ Invoked when the New button is triggered. """

        print("Doing New...")

    @observe('model.restart')
    def __on_restart_triggered(self, change):
        """ Invoked when the Restart Workflow button is triggered. """

        print("Doing Restart Workflow")

    @observe('model.scan')
    def __on_scan_triggered(self, change):
        """ Invoked when the Scan button is triggered. """

        print("Doing Scan")

    @observe('model.update')
    def __on_update_triggered(self, change):
        """ Invoked when the Update button is triggered. """

        print("Doing Update")

    def __on_versions_changed(self, change):
        """ Invoked when the list of project versions changes. """

        project = change.model

        if project == self.current_project:
            # See if the current working version has been removed.
            if self.current_project_ui.working_version in change.old:
                # FIXME: What else needs to happen when removing a version?
                self.current_project_ui.set_working_version()

            self._update_versions()

    def _update_versions(self):
        """ Update the GUI from the current project's list of versions. """

        self.model.working_version = None
        IOptionSelector(self.working_version_editor).options = reversed(
                self.current_project.versions)
        self.model.working_version = self.current_project_ui.working_version
        IView(self.working_version_editor).visible = (
                len(self.current_project.versions) != 0)
