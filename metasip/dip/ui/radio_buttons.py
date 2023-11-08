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


from .option_selector_factory import OptionSelectorFactory
from .i_radio_buttons import IRadioButtons


class RadioButtons(OptionSelectorFactory):
    """ The RadioButtons class implements a factory for selecting an option
    using a set of radio buttons.
    """

    # The interface that the view can be adapted to.
    interface = IRadioButtons

    # The name of the toolkit factory method.
    toolkit_factory = 'radio_buttons'

    # The orientation of the radio buttons.
    vertical = IRadioButtons.vertical

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        view.vertical = self.vertical


# Register the view factory.
RadioButtons.view_factories.append(RadioButtons)
