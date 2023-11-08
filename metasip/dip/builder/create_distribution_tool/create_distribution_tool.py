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


from ...model import Dict, implements, Model, observe
from ...publish import ISubscriber
from ...pui import Action
from ...shell import ITool
from ...ui import Application, IDisplay, IView

from .. import IBuilderProject, DistributionManager


@implements(ITool, ISubscriber)
class CreateDistributionTool(Model):
    """ The CreateDistributionTool class implements a shell tool that creates a
    distribution.
    """

    # The type of models we subscribe to.
    subscription_type = IBuilderProject

    # The distributions keyed by the action that creates it.
    _action_distribution_map = Dict()

    def __init__(self):
        """ Initialize the tool. """

        distributionmanager = DistributionManager().instance

        for distribution in distributionmanager.distributions:
            self._add_distribution(distribution)

        observe('distributions', distributionmanager,
                self.__distributions_changed)

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        enabled = (change.new.event == 'dip.events.active')

        for action in self._action_distribution_map.keys():
            action.enabled = enabled

    def __distributions_changed(self, change):
        """ Invoked when the list of distributions changes. """

        # FIXME: Handle the removal of distributions.

        for distribution in change.new:
            self._add_distribution(distribution)

    def _add_distribution(self, distribution):
        """ Add a distribution to the tool. """

        action = Action(
                text="Create {0} distribution...".format(
                        self._distribution_name(distribution)),
                enabled=False, when_triggered=self._create_distribution,
                within='dip.builder.collections.build')

        self._action_distribution_map[action] = distribution

        IView(self.shell).actions.append(action)

    def _create_distribution(self, action):
        """ Invoked to create a distribution. """

        distribution = self._action_distribution_map[action]
        project = self.subscription.model
        title = action.plain_text

        defaults = DistributionManager.get_defaults(project, distribution)

        try:
            created = distribution.create_distribution(project, defaults,
                    title, self.shell)
        except:
            import traceback

            Application.warning(title,
                    "There was an error creating the {0} distribution.".format(
                            self._distribution_name(distribution)),
                    parent=self.shell, detail=traceback.format_exc())
            return

        if created:
            Application.information(title,
                    "The {0} distribution was created successfully.".format(
                            self._distribution_name(distribution)),
                    parent=self.shell)

    @staticmethod
    def _distribution_name(distribution):
        """ Return a user friendly name for a distribution. """

        idisplay = IDisplay(distribution, exception=False)
        if idisplay is not None:
            name = idisplay.name
        else:
            id = distribution.id
            if id != '':
                name = id.split('.')[-1]
            else:
                name = str(distribution)

        return name
