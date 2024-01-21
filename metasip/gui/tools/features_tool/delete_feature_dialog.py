# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QCheckBox, QComboBox

from ...helpers import BaseDialog
from ...shell import EventType

from ..helpers import tagged_items

from .helpers import init_feature_selector


class DeleteFeatureDialog(BaseDialog):
    """ This class implements the dialog for deleting a feature. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        self._feature = QComboBox()
        layout.addWidget(self._feature)

        self._discard = QCheckBox(
                "Discard feature-specific parts of the project?")
        layout.addWidget(self._discard)

    def set_fields(self):
        """ Set the dialog's fields from the project. """

        init_feature_selector(self._feature, self.model)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        feature = self._feature.currentText()
        discard = self._discard.isChecked()

        # Delete from each API item it appears.
        remove_items = []

        for api_item, container in tagged_items(project):
            # Ignore items that aren't tagged with a feature.
            if len(api_item.features) == 0:
                continue

            remove_features = []

            for f in api_item.features:
                if f[0] == '!':
                    if f[1:] == feature:
                        # Just remove it if it is not the only one or if we are
                        # discarding if enabled (and the feature is inverted).
                        if len(api_item.features) > 1 or discard:
                            remove_features.append(f)
                        else:
                            remove_items.append((api_item, container))
                            break

                elif f == feature:
                    # Just remove it if it is not the only one or if we are
                    # discarding if enabled.
                    if len(api_item.features) > 1 or not discard:
                        remove_features.append(f)
                    else:
                        remove_items.append((api_item, container))
                        break
            else:
                # Note that we deal with a feature appearing multiple times,
                # even though that is probably a user bug.
                for f in remove_features:
                    api_item.features.remove(f)

        for api_item, container_item in remove_items:
            container_item.content.remove(api_item)
            self.shell.notify(EventType.CONTAINER_API_DELETE,
                    (container_item, api_item))

        # Delete from the project's list.
        if feature in project.externalfeatures:
            feature_list = project.externalfeatures
        else:
            feature_list = project.features

        feature_list.remove(feature)

        self.shell.notify(EventType.FEATURE_DELETE, feature)

        return True
