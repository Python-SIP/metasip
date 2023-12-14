# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


# In metasip prior to v2.12 the project format version was a single integer and
# some versions were known to require input from the user in order to update
# the project to that version.  For v2.8 and later the format version is a
# 2-tuple of major and minor version.  A change in the major version means user
# input is needed and a project cannot be used until the project is updated.  A
# change in the minor version means the project can be viewed and will only be
# updated to the latest minor version if the project is saved.
#
# A minimum project version is specified so that any version prior to this is
# not supported by metasip v2.12 and later.  An earlier version of metasip
# first be used to update the project to that version.  Old versions were never
# seen "in the wild" so there is no need to carry the baggage of supporting
# them in current code.
#
# The project format version is stored in the project differently according to
# the major version of the format.  For major version 0 it is stored in the
# 'version' attribute.  For other major versions it is stored in the
# 'majorversion' and 'minorversion' attributes.


# Project format version history:
#
#  0.16 Implemented by metasip v2.11.
#       - added pyssizetclean to the Module element.
#
#  0.15 Implemented by metasip v2.8.
#       - removed the 'version' attribute of the Module element.
#       - added the 'removed' value of the 'status' attribute.


# The oldest supported project format.
MinimumProjectVersion = (0, 15)

# The latest supported project format.
ProjectVersion = (0, 16)
