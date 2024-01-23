# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


def adapt(model, target_type=None):
    """ Return an adapter for a model adapted to its type or super-type. """

    from .adapter_map import ADAPTER_MAP

    if target_type is None:
        target_type = type(model)

    assert isinstance(model, target_type)

    adapter_factory = ADAPTER_MAP[target_type]

    return adapter_factory(model)
