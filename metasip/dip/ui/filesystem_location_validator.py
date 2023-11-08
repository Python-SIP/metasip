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


import os.path

from ..model import Bool, Enum, implements, Model

from .i_filesystem_location_editor import IFilesystemLocationEditor
from .i_validator import IValidator


@implements(IValidator)
class FilesystemLocationValidator(Model):
    """ The FilesystemLocationValidator class implements an editor validator
    for filesystem locations.
    """

    # The mode of the editor.  'open_file' means a single, existing file will
    # be obtained.  'save_file' means that a single file that may or may not
    # exist will be obtained.  'directory' means a single, existing directory
    # will be obtained.
    mode = IFilesystemLocationEditor.mode

    # This is set if a value is required.
    required = Bool(False)

    def configure(self, editor):
        """ Configure an editor to use this validator.

        :param editor:
            is the editor.
        """

    def validate(self, editor):
        """ Validate an editor.

        :param editor:
            is the editor.
        :return:
            a string describing why the value is invalid.  An empty string is
            returned if the value is valid.
        """

        value = editor.value

        if value == '':
            ok = not self.required
        else:
            if self.mode == 'open_file':
                ok = os.path.isfile(value)
            elif self.mode == 'directory':
                ok = os.path.isdir(value)
            else:
                ok = True

        if ok:
            invalid_reason = ''
        elif self.mode == 'open_file':
            invalid_reason = "the name of an existing file is required"
        elif self.mode == 'save_file':
            invalid_reason = "the name of a file is required"
        elif self.mode == 'directory':
            invalid_reason = "the name of an existing directory is required"

        return invalid_reason
