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


from ....model import Adapter, implements, Instance, observe
from ....ui import IEditor

from ... import IStorageBrowser


@implements(IStorageBrowser)
class FilesystemStorageBrowserAdapter(Adapter):
    """ This adapter is used explicitly to adapt a browser view to the
    IStorageBrowser interface.
    """

    # The file selector within the browser.
    _file_selector = Instance(IEditor)

    def __init__(self):
        """ Initialise the adapter. """

        observe('value', IEditor(self._file_selector), self.__file_changed)

    @IStorageBrowser.invalid_reason.getter
    def invalid_reason(self):
        """ Invoked to get the invalid reason. """

        editor = self._file_selector

        if editor.validator is None:
            return ''

        return editor.validator.validate(editor)

    def __file_changed(self, change):
        """ Invoked when the value of the file selector changes. """

        self.location = self.storage.explicit_location(change.new) if change.new != '' else None

    @_file_selector.default
    def _file_selector(self):
        """ Invoked to return the file selector. """

        return self.adaptee.views[0]
