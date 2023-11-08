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


import os

from ...model import implements, Model, observe
from ...publish import ISubscriber
from ...shell import ITool
from ...ui import Action, ActionCollection, Application

from .. import IBuilderProject

from .application_template import ApplicationTemplate


@implements(ITool, ISubscriber)
class CreateApplicationTool(Model):
    """ The CreateApplicationTool class implements a shell tool that creates an
    application script.
    """

    # The collection of actions.
    build_actions = ActionCollection('dip.builder.actions.create_application',
            '', text="Build", id='dip.builder.collections.build')

    # The create application script action.
    create_action = Action(text="Create application script...", enabled=False,
            id='dip.builder.actions.create_application')

    # The identifier of the tool.
    id = 'dip.builder.tools.create_application'

    # The type of models we subscribe to.
    subscription_type = IBuilderProject

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        self.create_action.enabled = (change.new.event == 'dip.events.active')

    @create_action.triggered
    def create_action(self):
        """ Invoked when the create application script action is triggered. """

        title = self.create_action.plain_text
        parent = self.shell

        # Get the application data from the user.
        template = ApplicationTemplate()

        if not template.populate(title, parent):
            return

        if os.path.exists(template.script_name):
            answer = Application.question(title,
                    "The file {0} already exists. Are you sure you "
                    "want to overwrite it?".format(template.script_name),
                    parent=parent)

            if answer != 'yes':
                return

        try:
            self.subscription.model.create_application(template)
        except:
            import traceback

            Application.warning(title,
                    "There was an error creating the application.",
                    parent=parent, detail=traceback.format_exc())
            return

        Application.information(title,
                "The file {0} was created successfuly.".format(
                        template.script_name),
                parent=parent)
