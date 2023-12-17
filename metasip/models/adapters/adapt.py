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


def adapt(model, target_type=None):
    """ Return an adapter for a model adapted to its type or super-type. """

    from .adapter_map import ADAPTER_MAP

    if target_type is None:
        target_type = type(model)

    assert isinstance(model, target_type)

    adapter_factory = ADAPTER_MAP[target_type]

    return adapter_factory(model)
