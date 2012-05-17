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


from dip.model import implements, Model, Str
from dip.ui import Application

from ..interfaces import IUpdate, IUpdateManager


@implements(IUpdateManager)
class UpdateManager(Model):
    """ The UpdateManager class is the default implementation of the project
    update manager.
    """

    # The title used in dialogs and wizards.
    window_title = Str("Updating Project")

    def update(self, root, update_to):
        """ Update a project to a later format.

        :param root:
            is the root element of the project.
        :param update_to:
            is the project version to update to.
        :return:
            True if the update was done or False if the user cancelled.
        """

        # Check that we know how to do the requested updates.
        update_from = int(root.get('version'))

        iupdates = []
        for format in range(update_from + 1, update_to + 1):
            for update in self.updates:
                iupdate = IUpdate(update)

                if iupdate.updates_to == format:
                    iupdates.append(iupdate)
                    break
            else:
                Application.warning(self.window_title,
                        "The project has format v{0} and needs to be updated "
                        "to v{1} but there is no update from v{2} to "
                        "v{3}.".format(update_from, update_to, format - 1,
                                format))

                return False

        # Create any views needed.
        need_wizard = False
        views = []
        for iupdate in iupdates:
            view = iupdate.create_view(root)
            views.append(view)

            if view is not None:
                need_wizard = True

        if need_wizard:
            from PyQt4.QtGui import QLabel

            from dip.pui import Wizard, WizardPage
            from dip.ui import IWizard

            intro = WizardPage(
                    view=QLabel("The project has format v{0} and needs to be "
                            "updated to v{1}.\n\n"
                            "This wizard will guide you through the different "
                            "steps\n"
                            "required to do the update.\n\n"
                            "Cancel the wizard if you do not want to update "
                            "the project.".format(update_from,
                                    update_to)),
                    title="Updating project from v{0} to v{1}".format(
                            update_from, update_to))

            pages = [intro]
            for v, view in enumerate(views):
                if view is not None:
                    page = WizardPage(view=view,
                            title="Updating project from v{0} to v{1}".format(
                                    update_from + v, update_from + v + 1),
                            subtitle=iupdate.instruction)

                    pages.append(page)

            wizard = Wizard(views=pages)

            if not IWizard(wizard).execute():
                return False
        else:
            button = Application.question(self.window_title,
                    "The project has format v{0} and needs to be updated to "
                    "v{1}. Do you want to update it?".format(update_from,
                            update_to))

            if button != 'yes':
                return False

        # Do the updates.
        for iupdate, view in zip(iupdates, views):
            iupdate.update(root, view)

        return True
