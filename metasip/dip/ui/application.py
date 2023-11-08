# Copyright (c) 2020 Riverbank Computing Limited.
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


from .i_application import IApplication
from .toolkits import UIToolkit


class Application:
    """ The Application class creates a singleton application that implements,
    or can be adapted to the :class:`~dip.ui.IApplication` interface.
    """

    def __new__(cls, argv=None, **properties):
        """ Create the application.

        :param argv:
            is the sequence of command line arguments.  By default
            :attr:`sys.argv` is used.
        :param \*\*properties:
            are the keyword arguments used as toolkit specific property names
            and values that are used to configure the application.
        :return:
            the application.
        """

        if argv is None:
            from sys import argv

        return IApplication(UIToolkit.application(argv, **properties))

    @staticmethod
    def error(title, text, parent=None, detail=''):
        """ Display an error message to the user.

        :param title:
            is the title, typically used as the title of a dialog.
        :param text:
            is the text of the error.
        :param parent:
            is the optional parent view.
        :param detail:
            is the optional additional detail.
        """

        return UIToolkit.error(title, text, parent, detail)

    @staticmethod
    def information(title, text, parent=None):
        """ Display a informational message to the user.

        :param title:
            is the title, typically used as the title of a dialog.
        :param text:
            is the text of the message.
        :param parent:
            is the optional parent view.
        """

        UIToolkit.information(title, text, parent)

    @staticmethod
    def question(title, text, parent=None, detail='', buttons=('no', 'yes')):
        """ Ask the user a question.

        :param title:
            is the title, typically used as the title of a dialog.
        :param text:
            is the text of the question.
        :param parent:
            is the optional parent view.
        :param detail:
            is the optional additional detail.
        :param buttons:
            is the sequence of buttons to display.  Possible buttons are 'yes',
            'no', 'cancel', 'save' and 'discard'.  The first in the sequence is
            used as the default.
        :return:
            The button that was pressed.
        """

        return UIToolkit.question(title, text, parent, detail, buttons)

    @staticmethod
    def warning(title, text, parent=None, detail=''):
        """ Display a warning message to the user.

        :param title:
            is the title, typically used as the title of a dialog.
        :param text:
            is the text of the warning.
        :param parent:
            is the optional parent view.
        :param detail:
            is the optional additional detail.
        """

        return UIToolkit.warning(title, text, parent, detail)
