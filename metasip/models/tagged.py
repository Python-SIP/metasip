# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass, field
from typing import List

from .version_range import VersionRange


@dataclass
class Tagged:
    """ This class is a mixin for APIs that are subject to tags (i.e. SIP's %If
    statement).
    """

    # The optional list of logically or-ed features that the API item is
    # limited to.  A feature may be preceded by "!" to indicate the logical
    # inverse.
    features: List[str] = field(default_factory=list)

    # The optional list of logically or-ed platforms that the API item is
    # limited to.  Note that SIP supports inverting a platform, as does the
    # MetaSIP platforms tool, but the MetaSIP UI for picking a platform doesn't
    # yet.
    platforms: List[str] = field(default_factory=list)

    # The optional list of logically and-ed version ranges.  Note that SIP
    # supports multiple ranges, as does the MetaSIP versions tool, but the
    # MetaSIP UI for picking a version range doesn't yet.
    versions: List[VersionRange] = field(default_factory=list)
