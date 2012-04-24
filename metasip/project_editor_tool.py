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


import glob
import os

from PyQt4.QtGui import QProgressDialog

from dip.model import Dict, implements, Instance
from dip.shell import BaseManagedModelTool, IManagedModelTool
from dip.ui import IDisplay

from .Project import Project
from .QtGUI import Navigation


@implements(IManagedModelTool, IDisplay)
class ProjectEditorTool(BaseManagedModelTool):
    """ The ProjectEditorTool implements the tool for editing a project. """

    # The tool's identifier.
    id = 'metasip.tools.project_editor'

    # The tool's name used in model manager dialogs and wizards.
    name = "MetaSIP project editor"

    # The project being edited.
    project = Instance(Project)

    # The dictionary of lists of argument names indexed by the C++ signature.
    webxml = Dict()

    def create_views(self, model):
        """ Create the views for editing a model. """

        self.project = model

        # Create the view.
        view = Navigation.NavigationPane(self)

        # Display the project.
        view.draw()

        return [view]

    def handles(self, model):
        """ Check that the tool can handle a model. """

        return isinstance(model, Project)

    def loadWebXML(self):
        """ Load, if not already done, and return the WebXML data. """

        return self.webxml

    @webxml.default
    def webxml(self):
        """ Invoked to load the WebXML data. """

        from .WebXML import WebXMLParser

        webxml_files = glob.glob(os.path.join(self.project.webxmldir, '*.xml'))
        progress = QProgressDialog(self)
        progress.setWindowTitle("Parsing WebXML Files")
        progress.setModal(True)
        progress.setTotalSteps(len(webxml_files))
        progress.setMinimumDuration(500)

        webxml = {}

        for step, webxml_file in enumerate(webxml_files):
            progress.setLabelText(os.path.basename(webxml_file))
            progress.setProgress(step)

            parser = WebXMLParser()
            parser.parse(webxml_file, webxml)

        progress.setProgress(len(webxml_files))

        return webxml
