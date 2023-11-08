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


from ....model import implements, Model
from ....pui import FilesystemLocationEditor, Form
from ....ui import FilesystemLocationValidator, UIToolkit

from ... import IFilterHints, IStorageBrowser, IStorageUi

from .filesystem_storage_browser_adapter import FilesystemStorageBrowserAdapter


@implements(IStorageUi)
class FilesystemStorageUi(Model):
    """ The FilesystemStorageUi class implements the storage-specific user
    interfaces.
    """

    def read_browser(self, default_location=None, hints=None):
        """ Create a view that allows the user to browse storage and select a
        read location.

        :param default_location:
            is an optional default location.
        :param hints:
            is an optional source of hints.
        :return:
            the view which must implement, or can be adapted to,
            :class:`~dip.io.IStorageBrowser`.
        """

        return self._create_browser(default_location, hints, 'open_file')

    def get_read_location(self, title, default_location=None, hints=None, parent=None):
        """ Get a new location from the user to read from.

        :param title:
            is the title, typically used as the title of a dialog.
        :param default_location:
            is an optional default location.
        :param hints:
            is an optional source of hints.
        :param parent:
            is the optional parent view.
        :return:
            the new location or ``None`` if the user cancelled.
        """

        pathname = UIToolkit.get_open_file(title,
                directory=self._get_pathname(default_location),
                filter=self._get_filter(hints), parent=parent)

        return self.storage.explicit_location(pathname) if pathname != '' else None

    def write_browser(self, default_location=None, hints=None):
        """ Create a view that allows the user to browse storage and select a
        write location.

        :param default_location:
            is an optional default location.
        :param hints:
            is an optional source of hints.
        :return:
            the view which must implement, or can be adapted to,
            :class:`~dip.io.IStorageBrowser`.
        """

        return self._create_browser(default_location, hints, 'save_file')

    def get_write_location(self, title, default_location=None, hints=None, parent=None):
        """ Get a new location from the user to write to.

        :param title:
            is the title, typically used as the title of a dialog.
        :param default_location:
            is an optional default location.
        :param hints:
            is an optional source of hints.
        :param parent:
            is the optional parent view.
        :return:
            the new location or ``None`` if the user cancelled.
        """

        pathname = UIToolkit.get_save_file(title,
                directory=self._get_pathname(default_location),
                filter=self._get_filter(hints), parent=parent)

        return self.storage.explicit_location(pathname) if pathname != '' else None

    def _create_browser(self, default_location, hints, mode):
        """ Create a filesystem browser. """

        # FIXME: make this declarative and not use dip.pui.  Probably means we
        # need to return a 2-tuple of the view factory and the initial value
        # for the model.  How the handle the adapter?
        validator = FilesystemLocationValidator(mode=mode, required=True)
        editor = FilesystemLocationEditor(filter=self._get_filter(hints),
                validator=validator)
        validator.configure(editor)
        editor.value = self._get_pathname(default_location)

        view = Form(labels=["File name"], views=[editor])

        # Create an adapter explicitly because we want to only adapt this
        # specific instance.
        adapter = FilesystemStorageBrowserAdapter(adaptee=view,
                storage=self.storage)
        IStorageBrowser(view, adapter=adapter)

        return view

    def _get_pathname(self, location):
        """ Get the pathname from an optional location. """

        return '' if location is None or location.storage is not self.storage else location.pathname

    @staticmethod
    def _get_filter(hints):
        """ Return the file name filter to use. """

        filter_hints = IFilterHints(hints, exception=False)

        return '' if filter_hints is None else filter_hints.filter
