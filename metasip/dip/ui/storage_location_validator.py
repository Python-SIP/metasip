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


from ..model import Bool, Enum, implements, Model, Str
from ..io import IoManager

from .i_storage_location_editor import IStorageLocationEditor
from .i_validator import IValidator


@implements(IValidator)
class StorageLocationValidator(Model):
    """ The StorageLocationValidator class implements an editor validator for
    storage locations.
    """

    # The identifier of the format.
    format = Str()

    # The mode of the editor.  'open' means an existing location will be
    # obtained.  'save' means that a location that may or may not exist will
    # be obtained.
    mode = IStorageLocationEditor.mode

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
            invalid_reason = "a storage location is required" if self.required else ''
        else:
            if self.mode == 'open':
                locations = IoManager.readable_locations_from_string(value,
                        self.format)
            else:
                locations = IoManager.writeable_locations_from_string(value,
                        self.format)

            nr_locations = len(locations)
            if nr_locations == 0:
                invalid_reason = "a valid {0} storage location is required".format("readable" if self.mode == 'open' else "writeable")
            elif nr_locations > 1:
                invalid_reason = "an unambiguous storage location is required"
            else:
                invalid_reason = ''

        return invalid_reason
