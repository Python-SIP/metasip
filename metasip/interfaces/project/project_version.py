# Copyright (c) 2020 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


# The current project file format version number.
#
# History:
#  15   Implemented by metasip v2.8.
#       - added the 'removed' value of the 'status' attribute.
#
#  14   Implemented by metasip v2.5.
#       - added the /ScopesStripped/ argument annotation.
#
#  13   Implemented by metasip v2.3.
#       - added enumclass to the Enum element.
#
#  12   Implemented by metasip v1.20.
#       - added final to the Method element.
#
#  11   Implemented by metasip v1.19.
#       - added uselimitedapi to the Module element.
#
#  10   Implemented by metasip v1.18.
#       - added pydefault to the Argument element.
#
#   9   Implemented by metasip v1.16.
#       - added typehintcode to the Class element.
#
#   8   Implemented by metasip v1.15.
#       - added exportedtypehintcode and typehintcode to the SipFile element.
#
#   7   Implemented by metasip v1.14.
#       - added virtualerrorhandler to the Module element.
#
#   6   Implemented by metasip v1.12.
#       - added callsuperinit to the Module element.
#
#   5   Implemented by metasip v1.11.
#       - added finalisationcode to the Class element.
#
#   4   Implemented by metasip v1.10.
#       - added convfromtypecode to the Class element.
#
#   3   Implemented by metasip v1.9.
#       - added the features and platforms attributes to the EnumValue element.
#
#   2   Implemented by metasip v1.2.
#       - removed the inputdir, outputdir and webxmldir attributes from the
#         Project element
#       - replaced all sgen and egen attributes with versions attributes
#       - replaced the ModuleHeaderFile element with the SipFile element
#       - moved appropriate attributes from the HeaderFile element to the
#         SipFile element
#       - added HeaderFileVersion as a sub-element of the HeaderFile element
#         moved appropriate attributes from the HeaderFile element to the
#         HeaderFileVersion sub-element
#       - added the scan attribute of the HeaderDirectory element.
#
#   1   Implemented prior to metasip v1.0.
#
#   0   The original undocumented version.
ProjectVersion = 15
