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


from .i_group_box import IGroupBox
from .single_subview_container_factory import SingleSubviewContainerFactory


class GroupBox(SingleSubviewContainerFactory):
    """ The GroupBox class arranges its contents in a group box. """

    # The interface that the view can be adapted to.
    interface = IGroupBox

    # The name of the toolkit factory method.
    toolkit_factory = 'group_box'


# Register the view factory.
GroupBox.view_factories.append(GroupBox)