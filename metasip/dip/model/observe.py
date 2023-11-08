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


from .change_trigger import ChangeTrigger, get_change_trigger
from .delegated_to import DelegatedTo
from .model_utils import (get_attribute_type, get_model_types,
        resolve_attribute_path)


# Ensure that a missing optional argument can be detected.
_missing = object()


def observe(name, model=_missing, observer=_missing, remove=False):
    """ An attribute of a model is observed and an observer called when its
    value changes.  This can also be used as a method decorator that uses the
    decorated method as the observer.

    :param name:
        is the name of the attribute in the model to observe.  This may be an
        :term:`attribute path`.  If the last part of the name is '*' then all
        the attributes are observed.
    :param model:
        is the :class:`~dip.model.Model` instance.  This must not be specified
        when used as a decorator.
    :param observer:
        is the callable that is called when the attribute's value changes.  The
        observer is passed an :class:`~dip.model.AttributeChange` instance as
        its argument.  This must not be specified when used as a decorator.
    :param remove:
        is set if the observer is to be removed.
    """

    # See if it is being used as a decorator.
    if model is _missing:
        if observer is not _missing:
            raise TypeError(
                    "observer must not be specified when used as a decorator")

        def decorator(observer):
            """ The decorator function. """

            # Get any existing observed attributes.
            attr_list = getattr(observer, '_dip_observed', None)

            if attr_list is None:
                setattr(observer, '_dip_observed', [name])
            else:
                attr_list.append(name)

            return observer

        return decorator

    # Find the containing model and name of the attribute that is to be
    # observed.
    name, model = resolve_attribute_path(name, model)

    types = get_model_types(type(model))

    if name == '*':
        for name, atype in types.items():
            _observe(name, model, observer, remove, atype)
    else:
        _observe(name, model, observer, remove, types[name])


def _observe(name, model, observer, remove, atype):
    """ Observe a single attribute of a model. """

    # Resolve any delegates.
    if isinstance(atype, DelegatedTo):
        model, name = atype.delegates_to(model)
        atype = get_attribute_type(model, name)

    # Get the trigger to communicate changes, creating it if necessary.
    trigger_name = '_dip_change_trigger_' + name
    trigger = model.__dict__.get(trigger_name)

    if trigger is None:
        trigger = ChangeTrigger()
        model.__dict__[trigger_name] = trigger

    observed_func = atype._observed_func

    if remove:
        trigger.remove_observer(observer)

        if observed_func is not None:
            observed_func(model, trigger.nr_observers)
    else:
        if observed_func is not None:
            observed_func(model, trigger.nr_observers + 1)

        trigger.add_observer(observer)


def notify_observers(name, model, new, old):
    """ Notify any observers about a change to the value of an attribute of a
    model.

    :param name:
        is the name of the attribute in the model.
    :param model:
        is the :class:`~dip.model.Model` instance.
    :param new:
        is the new value of the attribute.
    :param old:
        is the old value of the attribute.
    """

    trigger = get_change_trigger(model, name)

    if trigger is not None:
        # Avoid a circular import.
        from .attribute_change import AttributeChange

        trigger.change = AttributeChange(model=model, name=name, new=new,
                old=old)
