# Copyright (c) 2012 Riverbank Computing Limited.
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


from .instance import Instance
from .meta_interface import MetaInterface
from .meta_model import MetaModel


class MetaSingleton(MetaModel):
    """ The MetaSingleton class is the meta-class for Singleton and is
    responsible for enforcing the singleton behaviour and implementing a
    read-only proxy for the managed instance.
    """

    def __call__(cls, *args, **kwargs):
        """ This is called to create a new singleton instance or to return the
        one created previously.
        """

        if cls.singleton is None:
            cls.singleton = super().__call__(*args, **kwargs)

            # If the managed instance's type is defined as an interface then
            # save the type.
            cls._dip_iface = None

            declarative_type = cls.instance
            if isinstance(declarative_type, Instance):
                if len(declarative_type.types) == 1:
                    instance_type = declarative_type.types[0]
                    if isinstance(instance_type, MetaInterface):
                        cls._dip_iface = instance_type

        return cls.singleton

    def __getattr__(cls, name):
        """ This will ensure that a singleton exists and proxy any unknown
        attribute accesses to the managed instance.
        """

        if cls.singleton is None:
            cls()

        instance = cls.singleton.instance

        # Adapt the instance if it's type is defined as an interface.
        iface = cls._dip_iface
        if iface is not None:
            instance = iface(instance)

        return getattr(instance, name)
