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


from ..model import Bool

from .editor_factory import EditorFactory
from .i_filesystem_location_editor import IFilesystemLocationEditor


class FilesystemLocationEditor(EditorFactory):
    """ The FilesystemLocationEditor class implements a filesystem location
    editor factory.  Note that :class:`~dip.ui.StorageLocationEditor` should
    normally be used instead.
    """

    # The filter as defined by :attr:`~dip.io.IFilterHints.filter`.
    filter = IFilesystemLocationEditor.filter

    # The interface that the view can be adapted to.
    interface = IFilesystemLocationEditor

    # The mode of the editor.  'open_file' means a single, existing file will
    # be obtained.  'save_file' means that a single file that may or may not
    # exist will be obtained.  'directory' means a single, existing
    # directory will be obtained.
    mode = IFilesystemLocationEditor.mode

    # This is set if a value is required.
    required = Bool(False)

    # The name of the toolkit factory method.
    toolkit_factory = 'filesystem_location_editor'

    def initialise_view(self, view, model):
        """ Initialise the configuration as a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        view.filter = self.filter
        view.mode = self.mode

    def set_default_validator(self, view):
        """ Sets a view's default validator.

        :param view:
            is the view.
        """

        from .filesystem_location_validator import FilesystemLocationValidator

        view.validator = FilesystemLocationValidator(mode=self.mode,
                required=self.required)


# Register the view factory.
FilesystemLocationEditor.view_factories.append(FilesystemLocationEditor)
