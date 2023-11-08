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


class IFilesystemLocationEditor(IEditor):
    """ The IFilesystemLocationEditor interface defines the API to be
    implemented by a filesystem location editor.
    """

    # The filter as defined by :attr:`~dip.io.IFilterHints.filter`.
    filter = Str()

    # The mode of the editor.  'open_file' means a single, existing file will
    # be obtained.  'save_file' means that a single file that may or may not
    # exist will be obtained.  'directory' means a single, existing
    # directory will be obtained.
    mode = Enum('open_file', 'save_file', 'directory')
