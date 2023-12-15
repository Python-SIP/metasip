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


from ..dip.model import Interface, List, Str

from .version_range_model import VersionRangeModel


class TaggedMixin(Interface):
    """ This class is a mixin for APIs that are subject to tags (i.e. SIP's %If
    statement).
    """

    # The optional list of logically or-ed features that the API item is
    # limited to.  A feature may be preceded by "!" to indicate the logical
    # inverse.
    features = List(Str())

    # The optional list of logically or-ed platforms that the API item is
    # limited to.  Note that SIP supports inverting a platform, as does the
    # MetaSIP platforms tool, but the MetaSIP UI for picking a platform doesn't
    # yet.
    platforms = List(Str())

    # The optional list of logically and-ed version ranges.  Note that SIP
    # supports multiple ranges, as does the MetaSIP versions tool, but the
    # MetaSIP UI for picking a version range doesn't yet.
    versions = List(VersionRangeModel)
