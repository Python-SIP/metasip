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


from .box_layout_factory import BoxLayoutFactory
from .i_h_box import IHBox


class HBox(BoxLayoutFactory):
    """ The HBox class arranges its contents horizontally. """

    # The interface that the view can be adapted to.
    interface = IHBox

    # The name of the toolkit factory method.
    toolkit_factory = 'h_box'


# Register the view factory.
HBox.view_factories.append(HBox)
