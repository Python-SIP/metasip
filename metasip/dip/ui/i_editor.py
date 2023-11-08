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


from ..model import Any, Bool, Enum, Instance, Model, Str, TypeFactory

from .i_validator import IValidator
from .i_view import IView


class IEditor(IView):
    """ The IEditor interface defines the API to be implemented (typically
    using adaptation) by an :term:`editor`.
    """

    # The name of the attribute in the model the editor is bound to.  This is
    # not an :term:`attribute path`.
    attribute_name = Str()

    # The type of the attribute in the model.
    attribute_type = Instance(TypeFactory)

    # The model containing the attribute the editor is bound to.
    model = Instance(Model)

    # This is set if the editor is read-only.
    read_only = Bool(False)

    # This is set if the editor's value should be remembered between sessions.
    remember = Bool(False)

    # The policy a view should follow when handling the editor's title.
    # 'default' means that the editor doesn't embed the title and the view is
    # free to use it in any way.  'optional' means the editor embeds the title
    # but the view can ask for it to be removed.  'embedded' means the editor
    # embeds the title and the view cannot do anything with it.
    title_policy = Enum('default', 'optional', 'embedded')

    # The editor's validator.
    validator = Instance(IValidator)

    # The value of the editor.
    value = Any()

    def remove_title(self):
        """ Remove an editor's title.  This will only be called if the title
        policy is 'optional'.
        """
