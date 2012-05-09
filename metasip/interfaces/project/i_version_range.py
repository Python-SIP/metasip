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


from dip.model import Instance, Interface

from .i_version import IVersion


class IVersionRange(Interface):
    """ The IVersionRange interface is implemented by models that represent a
    range of versions.
    """

    # The end version.
    endversion = Instance(IVersion)

    # The start generation.
    startversion = Instance(IVersion)
