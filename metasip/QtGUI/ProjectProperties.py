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


from PyQt4.QtGui import QDialog, QFileDialog

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
        self.srcRootDir.setText(prj.inputdir)
        self.webXmlRootDir.setText(prj.webxmldir)

        for p in prj.platforms.split():
            self.platformTags.addItem(p)

        self.buttonRemovePlatTag.setEnabled(self.platformTags.count())
        self.buttonRemovePlatTag.clicked.connect(self._removePlatTag)

        for f in prj.features.split():
            self.featureTags.addItem(f)

        self.buttonRemoveFeatTag.setEnabled(self.featureTags.count())
        self.buttonRemoveFeatTag.clicked.connect(self._removeFeatTag)

        for f in prj.externalfeatures:
            self.extFeatureTags.addItem(f)

        self.buttonRemoveExtFeatTag.setEnabled(self.extFeatureTags.count())
        self.buttonRemoveExtFeatTag.clicked.connect(self._removeExtFeatTag)

        for m in prj.externalmodules:
            self.externalModules.addItem(m)

        self.buttonRemoveModule.setEnabled(self.externalModules.count())
        self.buttonRemoveModule.clicked.connect(self._removeModule)

        for n in prj.ignorednamespaces.split():
            self.ignoredNamespaces.addItem(n)

        self.buttonRemoveNamespace.setEnabled(self.ignoredNamespaces.count())
        self.buttonRemoveNamespace.clicked.connect(self._removeNamespace)

        if prj.sipcomments:
            self.sipFileComments.setPlainText(prj.sipcomments + "\n")

        self.browseSrcRootDir.clicked.connect(self._browse_src)
        self.browseWebXmlRootDir.clicked.connect(self._browse_webxml)

    def fields(self):
        """ Return a tuple of the dialog fields. """

        rootmodule = self.rootModule.text().strip()
        srcrootdir = self.srcRootDir.text().strip()
        webxmlrootdir = self.webXmlRootDir.text().strip()
        sipcomments = self.sipFileComments.toPlainText().strip()

        pl = [self.platformTags.itemText(i)
                for i in range(self.platformTags.count())]

        fl = [self.featureTags.itemText(i)
                for i in range(self.featureTags.count())]

        xfl = [self.extFeatureTags.itemText(i)
                for i in range(self.extFeatureTags.count())]

        ml = [self.externalModules.itemText(i)
                for i in range(self.externalModules.count())]

        ns = [self.ignoredNamespaces.itemText(i)
                for i in range(self.ignoredNamespaces.count())]

        return (rootmodule, srcrootdir, webxmlrootdir, ' '.join(pl),
                ' '.join(fl), xfl, ml, ' '.join(ns), sipcomments)

    def _removePlatTag(self):
        """
        Remove the current platform tag from the list.
        """
        idx = self.platformTags.currentIndex()

        if idx >= 0:
            self.platformTags.removeItem(idx)
            self.buttonRemovePlatTag.setEnabled(self.platformTags.count())

    def _removeFeatTag(self):
        """
        Remove the current feature tag from the list.
        """
        idx = self.featureTags.currectIndex()

        if idx >= 0:
            self.featureTags.removeItem(idx)
            self.buttonRemoveFeatTag.setEnabled(self.featureTags.count())

    def _removeExtFeatTag(self):
        """
        Remove the current external feature tag from the list.
        """
        idx = self.extFeatureTags.currectIndex()

        if idx >= 0:
            self.extFeatureTags.removeItem(idx)
            self.buttonRemoveExtFeatTag.setEnabled(self.extFeatureTags.count())

    def _removeModule(self):
        """
        Remove the current external module from the list.
        """
        idx = self.externalModules.currectIndex()

        if idx >= 0:
            self.externalModules.removeItem(idx)
            self.buttonRemoveModule.setEnabled(self.externalModules.count())

    def _removeNamespace(self):
        """
        Remove the current ignored namespace from the list.
        """
        idx = self.ignoredNamespaces.currectIndex()

        if idx >= 0:
            self.ignoredNamespaces.removeItem(idx)
            self.buttonRemoveNamespace.setEnabled(self.ignoredNamespaces.count())

    def _browse_src(self):
        """
        Handle the Browse source directory button.
        """
        d = QFileDialog.getExistingDirectory(self, "Source Root Directory",
                self.srcRootDir.text())

        if not d.isNull():
            self.srcRootDir.setText(d)

    def _browse_webxml(self):
        """
        Handle the Browse WebXML directory button.
        """
        d = QFileDialog.getExistingDirectory(self, "WebXML Root Directory",
                self.webXmlRootDir.text())

        if not d.isNull():
            self.webXmlRootDir.setText(d)
