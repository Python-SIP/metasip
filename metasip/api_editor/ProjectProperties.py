# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from PyQt6.QtWidgets import QDialog

from .Designer.ProjectPropertiesBase import Ui_ProjectPropertiesBase


class ProjectPropertiesDialog(QDialog, Ui_ProjectPropertiesBase):
    """ This class implements the dialog for a project's properties. """

    def __init__(self, prj, parent):
        """
        Initialise the dialog.

        prj is the project instance.
        parent is the parent widget.
        """
        super(ProjectPropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self.rootModule.setText(prj.rootmodule)

        for n in prj.ignorednamespaces:
            self.ignoredNamespaces.addItem(n)

        self.buttonRemoveNamespace.setEnabled(self.ignoredNamespaces.count())
        self.buttonRemoveNamespace.clicked.connect(self._removeNamespace)

        if prj.sipcomments:
            self.sipFileComments.setPlainText(prj.sipcomments + "\n")

    def fields(self):
        """ Return a tuple of the dialog fields. """

        rootmodule = self.rootModule.text().strip()
        sipcomments = self.sipFileComments.toPlainText().strip()

        ns = [self.ignoredNamespaces.itemText(i)
                for i in range(self.ignoredNamespaces.count())]

        return (rootmodule, ns, sipcomments)

    def _removeNamespace(self):
        """
        Remove the current ignored namespace from the list.
        """
        idx = self.ignoredNamespaces.currentIndex()

        if idx >= 0:
            self.ignoredNamespaces.removeItem(idx)
            self.buttonRemoveNamespace.setEnabled(self.ignoredNamespaces.count())
