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


import sys

from .. import TOOLKIT

from ..model import Singleton


class Toolkit(Singleton):
    """ The Toolkit class is a base class for :term:`toolkit` singletons. """

    def import_toolkit(self, package):
        """ Import a module containing a toolkit factory and create the toolkit
        from the factory.  The factory must be a module level callable called
        ``Toolkit``.

        :param package:
            the name of the package containing the different toolkits.
        :return:
            the toolkit.
        """

        # Import the module.
        toolkit_name = package + '.' + TOOLKIT
        __import__(toolkit_name)

        # Get the toolkit factory.
        module = sys.modules[toolkit_name]
        toolkit_factory = getattr(module, 'Toolkit')

        # Create the toolkit.
        return toolkit_factory()
