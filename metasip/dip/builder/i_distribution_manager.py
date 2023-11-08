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


from ..model import List, Interface

from .i_distribution import IDistribution


class IDistributionManager(Interface):
    """ The IDistributionManager interface defines the API of the object that
    manages the available distribution types.
    """

    # The list of available distribution types.
    distributions = List(IDistribution)

    def distribution(self, id):
        """ Find the distribution with a particular identifier.

        :param id:
            is the identifier.
        :return:
            the distribution or ``None`` if none was found.
        """

    def get_defaults(self, project, id):
        """ Get a set of defaults for a distribution from a project if they
        are present.

        :param project:
            is the project.
        :param id:
            is the identifier of the distribution.
        :return:
            the defaults.
        """

    def update_defaults(self, project, defaults):
        """ Update the set of defaults for a distribution in a project.

        :param project:
            is the project.
        :param defaults:
            is the model containing the defaults.
        """
