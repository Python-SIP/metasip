# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ...shell import EventType

from ..helpers import tagged_items, validate_identifier, validation_error


def init_version_selector(selector, project):
    """ Initialise a version selector. """

    selector.clear()
    selector.addItems(project.versions)


def validate_version_name(version, project, dialog):
    """ Validate a version name and return True if it is valid. """

    message = validate_identifier(version, "version")
    if message is None:
        if version in project.versions:
            message = "A version has already been defined with the same name."

    if message is not None:
        validation_error(message, dialog)
        return False

    return True


def delete_version(version, shell, *, migrate_items):
    """ Delete a version and all API items defined by it. """

    project = shell.project
    versions = project.versions

    removing_first_version = (version == versions[0])

    # Delete from each API item it appears.
    remove_items = []

    for api_item, container in tagged_items(project):
        # Ignore items that aren't tagged with a version.
        if len(api_item.versions) == 0:
            continue

        remove_ranges = []

        for r in api_item.versions:
            if r.startversion == version:
                # It now starts with the version after the one we are deleting.
                # If that is the same as the end version then we delete the API
                # item.
                new_start = '' if versions[-1] == version else versions[versions.index(version) + 1]

                if new_start == r.endversion:
                    remove_items.append((api_item, container))
                    break

                r.startversion = new_start

            # If the start version is now what the first version will now be
            # then we clear it.
            if r.startversion != '' and removing_first_version and r.startversion == versions[1]:
                r.startversion = ''

            if r.endversion == version:
                if migrate_items:
                    # It now ends with the version after the one we are
                    # deleting.
                    new_end = '' if versions[-1] == version else versions[versions.index(version) + 1]

                    r.endversion = new_end
                else:
                    remove_items.append((api_item, container))
                    break

            if r.startversion == '' and r.endversion == '':
                remove_ranges.append(r)
        else:
            for r in remove_ranges:
                api_item.versions.remove(r)

    for api_item, container_item in remove_items:
        container_item.content.remove(api_item)
        shell.notify(EventType.CONTAINER_API_DELETE,
                (container_item, api_item))

    # Delete from the header file versions.
    remove_hfile_versions = []
    removing_last_version = (len(project.versions) == 1)

    for hdir in project.headers:
        if version in hdir.scan:
            hdir.scan.remove(version)

        # If the versions to scan now just has a marker from when no versions
        # were defined, remove the marker so it doesn't suggest that any
        # remaining version needs scanning.
        if len(hdir.scan) == 1 and hdir.scan[0] == '':
            del hdir.scan[0]

        for hfile in hdir.content:
            if removing_last_version:
                if len(hfile.versions) != 0:
                    hfile.versions[0].version = ''
            else:
                for hfile_version in hfile.versions:
                    if hfile_version.version == version:
                        remove_hfile_versions.append((hfile_version, hfile))
                        break

    for hfile_version, hfile in remove_hfile_versions:
        hfile.versions.remove(hfile_version)

    # Delete from the project's list.
    versions.remove(version)
    shell.notify(EventType.VERSION_DELETE, version)
