# Copyright (c) 2010 Riverbank Computing Limited.
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


from .type_factory import TypeFactory


def clone_model(model):
    """ Create a clone of a model.  Note that individual attributes are not
    recursively cloned.

    :param model:
        is the :class:`~dip.model.Model` instance.
    :return:
        the clone.
    """

    model_type = type(model)
    clone = model_type()

    for aname in get_model_types(model_type).keys():
        setattr(clone, aname, getattr(model, aname))

    return clone


def resolve_attribute_path(name, model):
    """ Return the sub-model and name referenced by an :term:`attribute path`.

    :param name:
        is the name of the attribute and may be an attribute path.
    :param model:
        is the model.
    :return:
        the attribute name (which will not be an attribute path) and the
        sub-model.
    """

    path = name.split('.')

    for part in path[:-1]:
        model = getattr(model, part)

        if model is None:
            raise AttributeError(
                    "'{0}' sub-model of attribute path '{1}' is None".format(
                            part, name))

    return path[-1], model


def get_attribute_type(model, name):
    """ Get the :class:`~dip.model.TypeFactory` sub-class instance for an
    attribute of a model.

    :param model:
        is the :class:`~dip.model.Model` instance.
    :param name:
        is the name of the attribute (and may not be an :term:`attribute path`..
    :return:
        the attribute's type object.
    """

    atypes = get_model_types(type(model))

    try:
        atype = atypes[name]
    except KeyError:
        raise AttributeError(
                "model {0} has no attribute '{1}'".format(model, name))

    return atype


def get_model_types(model_type):
    """ Get a copy of the dictionary of :class:`~dip.model.TypeFactory`
    sub-class instances, keyed by attribute name, for a model type.

    :param model_type:
        is the :class:`~dip.model.Model` sub-class.
    :return:
        the dictionary of type objects.
    """

    try:
        types = getattr(model_type, '_dip_type_cache')
    except:
        raise TypeError(
                "sub-class of dip.model.Model expected, not '{0}'".format(
                        type(model_type).__name__))

    # Filter out any internal non-TypeFactory stuff.
    return {name: type for name, type in types.items()
            if isinstance(type, TypeFactory)}


def get_attribute_types(model, attribute_type_type=None):
    """ Get the :class:`~dip.model.TypeFactory` sub-class instances for all
    attributes of a model.

    :param model:
        is the model
    :param attribute_type_type:
        is the optional :class:`~dip.model.TypeFactory` sub-class.  If this is
        specified then only attributes of this type will be returned.
    :return:
        the list of attribute types.
    """

    atypes = []

    for name, atype in get_model_types(type(model)).items():
        if attribute_type_type is None or isinstance(atype, attribute_type_type):
            atypes.append(getattr(model, name))

    return atypes
