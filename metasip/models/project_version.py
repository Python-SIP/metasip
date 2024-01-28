# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


# In metasip prior to v2.12 the project format version was a single integer and
# some versions were known to require input from the user in order to update
# the project to that version.  For v2.12 and later the format version is a
# 2-tuple of major and minor version.  A change in the major version means user
# input is needed and a project cannot be used until the project is updated.  A
# change in the minor version means the project can be viewed and will only be
# updated to the latest minor version if the project is saved.
#
# A minimum project version is specified so that any version prior to this is
# not supported by metasip v2.12 and later.  An earlier version of metasip must
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
#  0.17 Implemented by metasip v2.13.
#       - Added 'comments' to the 'Class', 'Constructor', 'Destructor', 'Enum',
#         'EnumValue', 'Function', 'ManualCode', 'Method', 'Namespace',
#         'OpaqueClass', 'OperatorCast', 'OperatorFunction', 'OperatorMethod',
#         'Typedef' and 'Variable' elements.
#       - Added 'docstring' to the 'Typedef' element.
#       - Added 'keywordarguments' to the 'Module' element.
#       - Removed 'outputdirsuffix' from the 'Module' element.
#       - Added 'platforms' to the 'HeaderDirectory' element.
#       - Removed 'filefilter', 'inputdirsuffix' and 'parserargs' from the
#         'HeaderDirectory' element.
#
#  0.16 Implemented by metasip v2.11.
#       - Added 'pyssizetclean' to the 'Module' element.
#
#  0.15 Implemented by metasip v2.8.
#       - Removed 'version' from the 'Module' element.
#       - Added the 'removed' value of the 'status' attribute.


# The oldest supported project format.
MinimumProjectVersion = (0, 15)

# The latest supported project format.
ProjectVersion = (0, 17)
