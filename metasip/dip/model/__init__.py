# Copyright (c) 2017 Riverbank Computing Limited.
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


""" The :mod:`dip.model` module implements a declarative type system for
Python.
"""


from .adapt import adapt
from .adapter import Adapter, unadapted
from .any import Any
from .attribute_change import AttributeChange
from .bool import Bool
from .callable import Callable
from .collection_type_factory import CollectionTypeFactory
from .delegated_to import DelegatedTo
from .dict import Dict
from .enum import Enum
from .exceptions import ValidationError, ValidationTypeError
from .float import Float
from .implements import implements
from .instance import Instance
from .int import Int
from .interface import Interface
from .isadapted import isadapted
from .list import List
from .mapping_proxy import MappingProxy
from .meta_interface import MetaInterface
from .meta_model import MetaModel
from .meta_singleton import MetaSingleton
from .model import Model
from .model_utils import (clone_model, get_attribute_type, get_attribute_types,
        get_model_types, resolve_attribute_path)
from .mutable_type_factory import MutableTypeFactory
from .observe import notify_observers, observe
from .singleton import Singleton
from .set import Set
from .str import Str
from .subclass import Subclass
from .trigger import Trigger
from .tuple import Tuple
from .type_factory import TypeFactory
from .value_type_factory import ValueTypeFactory
