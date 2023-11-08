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


from ..model import Bool, Enum, Str

from .i_editor import IEditor


class IStorageLocationEditor(IEditor):
    """ The IStorageLocationEditor interface defines the API to be implemented
    by a storage location editor.
    """

    # The filter hints as defined by :attr:`~dip.io.IFilterHints.filter`.
    filter_hints = Str()

    # The identifier of the format.
    format = Str()

    # The mode of the editor.  'open' means an existing location will be
    # obtained.  'save' means that a location that may or may not exist will be
    # obtained.
    mode = Enum('open', 'save')
