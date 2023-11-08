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


from .i_message_area import IMessageArea
from .view_factory import ViewFactory


class MessageArea(ViewFactory):
    """ The MessageArea class is a factory for a message area, which will be an
    implementation of, or something that be adapted to,
    :class:`~dip.ui.IMessageArea` to be used by a controller to display
    messages to the user.
    """

    # The interface that the view can be adapted to.
    interface = IMessageArea

    # The text displayed in the message area.
    text = IMessageArea.text

    # The name of the toolkit factory method.
    toolkit_factory = 'message_area'

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        view.text = self.text


# Register the view factory.
MessageArea.view_factories.append(MessageArea)
