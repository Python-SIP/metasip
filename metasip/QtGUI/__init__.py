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


""" This module implements the Qt GUI. """


import sys
import glob
import os

from PyQt4.QtCore import QDir, QSettings, Qt
from PyQt4.QtGui import (QAbstractSlider, QApplication, QFileDialog,
        QMainWindow, QMessageBox, QPlainTextEdit, QProgressDialog, QSplitter)

from dip.io import StorageError

from ..dip_future import io_IoManager_read, io_IoManager_write
from ..logger import Logger
from ..Project import Project
from ..WebXML import WebXMLParser

from .Designer.MainWindowBase import Ui_MainWindowBase
from .Navigation import NavigationPane


class Application(QApplication):
    """
    This class implements the GUI application.
    """
    def setMainWindow(self, mw):
        """
        Set the application's main window.

        mw is the main window instance.
        """
        mw.show()

    def execute(self):
        """
        Enter the GUI event loop and return it's result.
        """
        return self.exec_()


class MainWindow(QMainWindow, Ui_MainWindowBase):
    """
    This class implements the application's main window.
    """
    _fileFilter = "MetaSIP projects (*.msp)"

    def __init__(self, parent=None):
        """
        Initialise the main window.
        """
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)

        # This instance is the logger.
        Logger().instance = self

        self.project = None
        self._webxml = None

        # Initialise the different panes of the GUI.
        self._panes = []

        # Construct the rest of the GUI.
        self._splitter = QSplitter(Qt.Vertical, self)

        self._panes.append(NavigationPane(self, self._splitter))

        self._log = QPlainTextEdit(self._splitter, readOnly=True)

        self.setCentralWidget(self._splitter)

        # Get the user settings and adjust the layout.
        self._settings = QSettings('riverbankcomputing.com', 'MetaSIP')
        self._loadGUILayout()

    def closeEvent(self, ev):
        """
        Invoked when the user closes the window.
        """

        if not self._saveCurrent("Quit"):
            ev.ignore()

    def fileNew(self):
        """
        Handle the File/New action.
        """
        self.loadProject(Project(), "New Project")

    def fileOpen(self):
        """
        Handle the File/Open action.
        """
        fn = QFileDialog.getOpenFileName(self, "Open", self._getStartDir(),
                self._fileFilter)
        fn = str(fn)

        if fn:
            self.loadProject(Project(fn), "Open Project")

    def fileSave(self, saveas=None):
        """ Handle the File/Save action.

        :param saveas:
            is the optional name of the file to save the project as.
        """

        location = self.project.name if saveas is None else saveas

        try:
            io_IoManager_write(self.project, 'metasip.formats.project',
                    location)
        except StorageError as e:
            QMessageBox.critical(self, "Save Project", e.error,
                    QMessageBox.Ok|QMessageBox.Default, QMessageBox.NoButton)

    def fileSaveAs(self):
        """
        Handle the File/Save As action.
        """
        fn = QFileDialog.getSaveFileName(self, "Save As", self._getStartDir(),
                self._fileFilter)
        fn = str(fn)

        if fn:
            self.fileSave(fn)
            self._update()

    def fileExit(self):
        """
        Handle the File/Quit action.
        """
        caption = "Quit"

        if self._saveCurrent(caption):
            # Save the GUI layout and make sure the settings are written.
            self._saveGUILayout()
            del self._settings

            # Terminate normally.
            QApplication.quit()
            return

        ans = QMessageBox.question(self, caption,
                                   self.project.diagnostic + "\n\nDo you still want to leave the application?",
                                   QMessageBox.Yes|QMessageBox.Default,
                                   QMessageBox.No|QMessageBox.Escape)

        if ans == QMessageBox.Yes:
            QApplication.exit(1)

    def log(self, msg):
        """
        Write a message to the log window.
    
        msg is the text of the message and should not include explicit
        newlines.
        """
        # Update the text.
        self._log.appendPlainText(msg)

        # Make sure the new text is visible.
        self._log.verticalScrollBar().triggerAction(
                QAbstractSlider.SliderToMaximum)

        # Update the screen.
        QApplication.processEvents()

    def loadWebXML(self):
        """
        Load and return the WebXML data if not already done.
        """
        if self._webxml is None:
            # A dictionary of lists of argument names indexed by the C++
            # signature
            self._webxml = {}

            webxml_files = glob.glob(os.path.join(self.project.webxmldir, '*.xml'))
            progress = QProgressDialog(self)
            progress.setWindowTitle("Parsing WebXML Files")
            progress.setModal(True)
            progress.setTotalSteps(len(webxml_files))
            progress.setMinimumDuration(500)

            for step, webxml in enumerate(webxml_files):
                progress.setLabelText(os.path.basename(webxml))
                progress.setProgress(step)

                parser = WebXMLParser()
                parser.parse(webxml, self._webxml, self)

            progress.setProgress(len(webxml_files))

        return self._webxml

    def loadProject(self, prj, caption=''):
        """
        Load a project.

        prj is the Project instance.
        caption is the optional dialog caption.
        """
        # Save any current project.
        if not self._saveCurrent(caption):
            ans = QMessageBox.question(self, caption,
                                       self.project.diagnostic + "\n\nDo you still want to load the new project?",
                                       QMessageBox.Yes|QMessageBox.Default,
                                       QMessageBox.No|QMessageBox.Escape)

            if ans == QMessageBox.No:
                return

        if prj.name is not None:
            try:
                prj = io_IoManager_read(prj, 'metasip.formats.project',
                        prj.name)
            except StorageError as e:
                QMessageBox.critical(self, caption, prj.diagnostic,
                        QMessageBox.Ok|QMessageBox.Default,
                        QMessageBox.NoButton)

            return

        self.project = prj
        self._clearProject()
        self._draw()
        self._update(False)

    def _saveCurrent(self, caption):
        """
        Save any current project and return True if it was successful.

        caption is the text of the dialog caption.
        """
        # There is nothing to do if there is no current project or it hasn't
        # been modified.
        if not self.project or not self.project.hasChanged():
            return True

        ans = QMessageBox.question(self, caption,
                                   "The project has been modified.  Do you want to save it?",
                                   QMessageBox.Yes|QMessageBox.Default,
                                   QMessageBox.No|QMessageBox.Escape)

        if ans == QMessageBox.No:
            return True

        return self.project.save()

    def _draw(self):
        """
        Draw the current project.
        """
        for p in self._panes:
            p.draw()

    def _clearProject(self):
        """
        Clear the GUI so that it is ready to load a new project.
        """
        for p in self._panes:
            p.clearProject()

    def _getStartDir(self):
        """
        Return the name of the current directory (ie. the one containing the
        current project, or the current working directory).
        """
        if self.project.name:
            return os.path.dirname(self.project.name)

        return os.getcwd()

    def _update(self, dopanes=True):
        """
        Update the menus and other parts of the GUI after a possible change of
        project status.

        dopanes is True if the GUI panes should re-draw the project name.
        """
        self.setWindowTitle("MetaSIP - " + self.project.descriptiveName())
        self.actionSave.setEnabled(not not self.project.name)

        if dopanes:
            for p in self._panes:
                p.refreshProjectName()

    def _loadGUILayout(self):
        """
        Load the GUI layout from the user settings.
        """
        settings = self._settings

        settings.beginGroup('GUI')

        self.restoreState(settings.value('mainState'))
        self.restoreGeometry(settings.value('mainGeometry'))
        self._splitter.restoreState(settings.value('mainSplitter'))

        for pnr, p in enumerate(self._panes):
            settings.beginGroup('mainPane%u' % pnr)
            p.loadGUILayout(self._settings)
            settings.endGroup()

        settings.endGroup()

    def _saveGUILayout(self):
        """
        Save the GUI layout to the user settings.
        """
        settings = self._settings

        settings.beginGroup('GUI')

        settings.setValue('mainState', self.saveState())
        settings.setValue('mainGeometry', self.saveGeometry())
        settings.setValue('mainSplitter', self._splitter.saveState())

        for pnr, p in enumerate(self._panes):
            settings.beginGroup('mainPane%u' % pnr)
            p.saveGUILayout(self._settings)
            settings.endGroup()

        settings.endGroup()
