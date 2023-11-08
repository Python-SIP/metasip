# Copyright (c) 2012 Riverbank Computing Limited.
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


from ...model import clone_model, implements, Model

from .. import IDistributionManager


@implements(IDistributionManager)
class DistributionManager(Model):
    """ The DistributionManager class is the default implementation of the
    :class:`~dip.builder.IDistributionManager` interface.
    """

    def distribution(self, id):
        """ Find the distribution with a particular identifier.

        :param id:
            is the identifier.
        :return:
            the distribution or ``None`` if none was found.
        """

        for distribution in self.distributions:
            if distribution.id == id:
                break
        else:
            distribution = None

        return distribution

    def get_defaults(self, project, distribution):
        """ Get a set of defaults for a distribution from a project if they
        are present.

        :param project:
            is the project.
        :param distribution:
            is the distribution.
        :return:
            the defaults.
        """

        id = distribution.id

        for deflts in project.distributions_defaults:
            if deflts.id == id:
                defaults = clone_model(deflts)
                break
        else:
            defaults = self.distribution(id).defaults_factory()

        return defaults

    def update_defaults(self, project, defaults):
        """ Update the set of defaults for a distribution in a project.

        :param project:
            is the project.
        :param defaults:
            is the model containing the defaults.
        """

        # Remove any old defaults.
        id = defaults.id

        for deflts in project.distributions_defaults:
            if deflts.id == id:
                project.distributions_defaults.remove(deflts)
                break

        project.distributions_defaults.append(defaults)
