# Copyright (c) 2018 Riverbank Computing Limited.
#
# This file is part of dip.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from .any import Any
from .bool import Bool
from .dict import Dict
from .float import Float
from .int import Int
from .list import List
from .model import Model
from .set import Set
from .str import Str


class MappingProxy:
    """ The MappingProxy class implements a :class:`~dip.model.Model` based
    proxy for a mapping type.  It is assumed that the mapping has string keys.
    Note that changes made to the object being proxied cannot be observed.
    """

    def __new__(cls, mapping):
        """ Create the proxy.  We make modifications to the class dictionary
        that are specific to the mapping, therefore we need to create a new
        type each time.
        """

        cls_dict = {
            '__init__': _proxy__init__,
            '__getattr__': _proxy__getattr__,
            '__setattr__': _proxy__setattr__
        }

        metatype = type(Model)
        proxy_cls = metatype('MappingProxy', (Model, ), cls_dict)
        proxy = proxy_cls(mapping)

        return proxy


def _proxy__init__(self, mapping):
    """ Initialise the proxy. """

    self.__dict__['_dip_mapping'] = mapping

    # Create the types cache with a type for each entry in the mapping.
    atypes = {}

    for name, value in mapping.items():
        type_type = Any

        if value is not None:
            py_type = type(value)

            for builtin_type, type_type in _builtin_type_map:
                if issubclass(py_type, builtin_type):
                    break

        atype = type_type()
        atype.name = name

        atypes[name] = atype

    setattr(self.__class__, '_dip_type_cache', atypes)


def _proxy__getattr__(self, name):
    """ Get an attribute from the mapping. """

    return self.__dict__['_dip_mapping'][name]


def _proxy__setattr__(self, name, value):
    """ Set an attribute of the mapping. """

    # setattr() is called by the meta-type before __init__() so we might not
    # know about the mapping yet.  It will be setting the initial value which
    # should be ignored anyway.
    try:
        mapping = self.__dict__['_dip_mapping']
    except KeyError:
        pass
    else:
        mapping[name] = value


# The map of the types used to handle each supported builtin type.  Note that
# the order is important so we don't use a dict.
_builtin_type_map = (
    (bool,  Bool),
    (float, Float),
    (int,   Int),
    (str,   Str),
    (dict,  Dict),
    (list,  List),
    (set,   Set)
)
