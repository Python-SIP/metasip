# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QCheckBox, QComboBox

from ...helpers import BaseDialog
from ...shell import EventType

from ..helpers import tagged_items

from .helpers import init_platform_selector


class DeletePlatformDialog(BaseDialog):
    """ This class implements the dialog for deleting a platform. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        self._platform = QComboBox()
        layout.addWidget(self._platform)

        self._discard = QCheckBox(
                "Discard platform-specific parts of the project?")
        layout.addWidget(self._discard)

    def set_fields(self):
        """ Set the dialog's fields from the project. """

        init_platform_selector(self._platform, self.model)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        platform = self._platform.currentText()
        discard = self._discard.isChecked()

        # Delete from each API item it appears.
        remove_items = []

        for api_item, container in tagged_items(project):
            # Ignore items that aren't tagged with a platform.
            if len(api_item.platforms) == 0:
                continue

            remove_platforms = []

            for p in api_item.platforms:
                if p[0] == '!':
                    if p[1:] == platform:
                        # Just remove it if it is not the only one or if we are
                        # discarding if enabled (and the platform is inverted).
                        if len(api_item.platforms) > 1 or discard:
                            remove_platforms.append(f)
                        else:
                            remove_items.append((api_item, container))
                            break

                elif p == platform:
                    # Just remove it if it is not the only one or if we are
                    # discarding if enabled.
                    if len(api_item.platforms) > 1 or not discard:
                        remove_platforms.append(f)
                    else:
                        remove_items.append((api_item, container))
                        break
            else:
                # Note that we deal with a platform appearing multiple times,
                # even though that is probably a user bug.
                for p in remove_platforms:
                    api_item.platforms.remove(p)

        for api_item, container_item in remove_items:
            container_item.content.remove(api_item)
            self.shell.notify(EventType.CONTAINER_API_DELETE,
                    (container_item, api_item))

        # Delete from the project's list.
        project.platforms.remove(platform)

        self.shell.notify(EventType.PLATFORM_DELETE, platform)

        return True
