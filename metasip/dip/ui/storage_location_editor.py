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
from .i_storage_location_editor import IStorageLocationEditor


#FIXME: move to dip.io?
class StorageLocationEditor(EditorFactory):
    """ The StorageLocationEditor class implements a storage location editor
    factory.
    """

    # The filter hints as defined by :attr:`~dip.io.IFilterHints.filter`.
    filter_hints = IStorageLocationEditor.filter_hints

    # The identifier of the format.
    format = IStorageLocationEditor.format

    # The interface that the view can be adapted to.
    interface = IStorageLocationEditor

    # The mode of the editor.  'open' means an existing location will be
    # obtained.  'save' means that a location that may or may not exist will be
    # obtained.
    mode = IStorageLocationEditor.mode

    # This is set if a value is required.
    required = Bool(False)

    # The name of the toolkit factory method.
    toolkit_factory = 'storage_location_editor'

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        view.filter_hints = self.filter_hints
        view.format = self.format
        view.mode = self.mode

    def set_default_validator(self, view):
        """ Sets a view's default validator.

        :param view:
            is the view.
        """

        from .storage_location_validator import StorageLocationValidator

        return StorageLocationValidator(format=self.format, mode=self.mode,
                required=self.required)


# Register the view factory.
StorageLocationEditor.view_factories.append(StorageLocationEditor)
