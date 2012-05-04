# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.model import Enum

from .i_access import IAccess


class IExtendedAccess(IAccess):
    """ The IExtendedAccess interface is implemented by API items subject to
    the extended (i.e. Qt specific) C++ access specifiers.
    """

    # The access specifier.  An empty string means public.
    access = Enum('', 'protected', 'protected slots', 'private',
            'public slots', 'signals')
