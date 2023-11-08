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


from ..model import List, Interface, Str

from .i_python_class import IPythonClass


class IApplicationTemplate(Interface):
    """ The IApplicationTemplate interface defines the data needed to create
    an application script.
    """

    # The interpreter executable.
    interpreter = Str(
            tool_tip="The name of the Python interpreter to use",
            whats_this="This is the name of the Python interpreter to use to "
                    "execute the application.  It is placed after #! in the "
                    "first line of the application.")

    # The list of plugins.
    plugins = List(IPythonClass)

    # The name of the application script.
    script_name = Str(required='stripped',
            tool_tip="The name of the script",
            whats_this="This is the name of the application's executable "
                    "script.")

    # The application's window title.
    title_bar_text = Str(
            tool_tip="The contents of the application's title bar",
            whats_this="This is the text that will appear in the "
                    "application's title bar.""")
