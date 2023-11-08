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


from ...toolkits import ToolkitError


class Qt5ToolkitError(ToolkitError):
    """ The Qt5ToolkitError class is an exception raised when there is an error
    related to the Qt5 toolkit.
    """

    def __init__(self, error):
        """ Initialise the exception.

        :param error:
            is a string describing the error.  It is available as the *error*
            attribute.
        """

        super().__init__('qt5', error)


class Qt5ToplevelWidgetError(Qt5ToolkitError):
    """ The Qt5ToplevelWidgetError class is an exception raised when attempting
    to create a widget other than at the top level when the widget can only be
    used as a top-level widget.
    """

    def __init__(self, widget_type):
        """ Initialise the exception.

        :param widget_type:
            is the type of the widget.
        """

        super().__init__("{1} can only be used as a top-level widget".format(
                widget_type))

