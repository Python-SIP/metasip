# Copyright (c) 2011 Riverbank Computing Limited.
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


# The adapter targets keyed by the target interface.  A value is a list of
# 2-tuple of adapted type or interface and factory (i.e. Adapter sub-class).
_adapter_targets = {}


def add_adapter_factory(factory, adapted, interface):
    """ An internal function that registers an adapter factory (i.e. a
    sub-class of Adapter) for an adapted type and an interface.
    """

    new_af_pair = (adapted, factory)
    new_af_pair_list = [new_af_pair]

    af_pair_list = _adapter_targets.setdefault(interface, new_af_pair_list)

    if af_pair_list is not new_af_pair_list:
        # There was already an entry for the interface so update it.
        af_pair_list.append(new_af_pair)


def adapt_explicitly(adaptee, interface, adapter):
    """ An internal function that adapts an object to an interface using an
    explicit adapter.
    """

    _cache_adapter(_get_adapter_cache(adaptee), adaptee, interface, adapter)


def _cache_adapter(adapter_cache, adaptee, interface, adapter):
    """ Save an adapter/interface pair in an object's adapter cache. """

    # If this is the first adapter then save the cache.
    if len(adapter_cache) == 0:
        setattr(adaptee, '_dip_adapters', adapter_cache)

    adapter_cache.append((adapter, interface))


def _get_adapter_cache(adaptee):
    """ Return the adapter cache for an object. """

    # We keep the adapter cache in the object itself so that the adapter and
    # adaptee reference each other.  They will get garbage collected if nothing
    # else is referencing either of them.
    return getattr(adaptee, '_dip_adapters', [])


def _find_adapter(adaptee, interface, exception=False):
    """ Find an existing adapter that adapts an object to an interface. """

    adapter_cache = _get_adapter_cache(adaptee)

    # Use an existing adapter if possible.
    for adapter, iface in adapter_cache:
        # An existing adapter for an exact or more specific interface is fine.
        if issubclass(iface, interface):
            return adapter, adapter_cache

        # An existing adapter for a less specific interface is an error because
        # creating an adapter for the required interface would result in
        # duplication of any state held in the existing adapter.
        if issubclass(interface, iface):
            if exception:
                raise TypeError(
                        "'{0}' cannot be adapted to '{1}' because it has "
                        "already been adapted to '{2}'".format(
                                type(adaptee).__name__, interface.__name__,
                                iface.__name__))

            break

    return None, adapter_cache


def object_adapter(adaptee, interface, adapt, cache, exception):
    """ An internal function to return an adapter that adapts an object to an
    interface, creating it if necessary.
    """

    # Find any existing adapter.
    adapter, adapter_cache = _find_adapter(adaptee, interface, exception)
    if adapter is not None:
        return adapter

    # Find candidate adapter factories giving preference to exact matches.
    candidates = []
    for iface, af_pair_list in _adapter_targets.items():
        if iface is interface:
            candidates.insert(0, (iface, af_pair_list))
        elif issubclass(iface, interface):
            candidates.append((iface, af_pair_list))

    adaptee_type = type(adaptee)
    adaptee_interfaces = getattr(adaptee_type, '_dip_interfaces', ())
    adapted_interfaces = [iface for _, iface in adapter_cache]

    for iface, af_pair_list in candidates:
        # Try the adaptee's type.
        factory = _pick_factory(adaptee, [adaptee_type], af_pair_list)
        if factory is not None:
            break

        # Try the interfaces that the adaptee directly implements.
        factory = _pick_factory(adaptee, adaptee_interfaces, af_pair_list)
        if factory is not None:
            break

        # Try the interfaces that the adaptee has already been adapted to.
        factory = _pick_factory(adaptee, adapted_interfaces, af_pair_list)
        if factory is not None:
            break
    else:
        factory = None

    if factory is None:
        if exception:
            raise TypeError(
                    "'{0}' does not implement '{1}' and could not be "
                    "adapted".format(
                            type(adaptee).__name__, interface.__name__))

        return None

    if adapt:
        # Create the adapter.
        adapter = factory(adaptee=adaptee)

        if cache:
            _cache_adapter(adapter_cache, adaptee, iface, adapter)

    return adapter


def _pick_factory(adaptee, from_types, af_pair_list):
    """ Pick a factory to adapt one of a number of types from a list of
    type/factory pairs.
    """

    for from_type in from_types:
        # Find candidate factories giving preference to exact matches.  If
        # there is no exact match then pick the first one found.
        candidates = []
        for adapted, factory in af_pair_list:
            if from_type is adapted:
                if factory.isadaptable(adaptee):
                    candidates.insert(0, factory)
                    break

            if issubclass(from_type, adapted):
                if factory.isadaptable(adaptee):
                    candidates.append(factory)

        if len(candidates) > 0:
            return candidates[0]

    return None
