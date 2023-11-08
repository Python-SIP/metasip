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


from ..model import Enum

from .editor_factory import EditorFactory
from .i_line_editor import ILineEditor


class LineEditor(EditorFactory):
    """ The LineEditor class implements a line editor factory for string
    attributes.
    """

    # The interface that the view can be adapted to.
    interface = ILineEditor

    # This specifies whether or not a value is required.  It is ignored if a
    # validator is explicitly set.  'no' means that a value is not required
    # (i.e. it can be an empty string).  'yes' means that a value is required.
    # 'stripped' means that a value with no leading or trailing whitespace is
    # required.  If it is not explicitly set then any corresponding value in
    # the type's meta-data is used.
    required = Enum('no', 'yes', 'stripped', allow_none=True)

    # The name of the toolkit factory method.
    toolkit_factory = 'line_editor'

    def set_default_validator(self, view):
        """ Sets a view's default validator.

        :param view:
            is the view.
        """

        # See if a value is required.
        required = self.required
        if required is None:
            attribute_type = view.attribute_type
            if attribute_type is not None:
                required = attribute_type.metadata.get('required')

            if required is None:
                required = 'no'

        # See if a validator is required.
        if required in ('yes', 'stripped'):
            from .string_validator import StringValidator

            view.validator = StringValidator(stripped=(required == 'stripped'))


# Register the view factory.
LineEditor.view_factories.append(LineEditor)
