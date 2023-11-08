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


from .i_automated import IAutomated


class IAutomatedOptionSelector(IAutomated):
    """ The IAutomatedOptionSelector interface defines the API of automated
    editors that handle lists of options.
    """

    def simulate_select(self, id, delay, index):
        """ Simulate the user selecting an option.

        :param id:
            is the (possibly scoped) identifier of the widget.  This is
            normally used in exceptions.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param value:
            is the value of the option.
        """
