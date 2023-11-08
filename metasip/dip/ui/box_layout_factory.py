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


from .container_factory import ContainerFactory
from .stretch import Stretch


class BoxLayoutFactory(ContainerFactory):
    """ The BoxLayoutFactory class is the base class for all factories that
    create views that can contain :class:`~dip.ui.Stretch`.
    """

    def create_additional_content(self, content):
        """ Create additional content to be added to the list of sub-views.

        :param content:
            the content from which additional content can be created.
        :return:
            the additional content.
        """
        
        if isinstance(content, Stretch):
            return content

        raise TypeError("the contents of a view must be either an instance of "
                "a ViewFactory sub-class, a string or Stretch, not "
                "'{0}'".format(type(content).__name__))
