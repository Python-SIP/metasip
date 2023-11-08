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


from ...model import implements
from ...shell.tools.form import FormTool
from ...ui import IDisplay

from .. import IBuilderProject


@implements(IDisplay)
class IBuilderProjectTool(FormTool):
    """ The IBuilderProjectTool class implements an editor for models that
    implement the IBuilderTool interface.
    """

    # The tool's identifier.
    id = 'dip.builder.tools.project_editor'

    # The sub-class of Model that the tool can handle.
    model_type = IBuilderProject

    # The name of the tool.
    name = "Builder project editor"

    @FormTool.view_factory.default
    def view_factory(self):
        """ Invoked to return the default view factory. """

        from ...ui import (FilesystemLocationEditor, Form, MessageArea,
                Stretch, TextEditor, VBox)

        return VBox(
                Form('description', 'author', 'author_email', 'home_page',
                        TextEditor('file_header_text'),
                        FilesystemLocationEditor('package_directory',
                                mode='directory')),
                Stretch(), MessageArea())
