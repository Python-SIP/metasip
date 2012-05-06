# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.model import Singleton


class Logger(Singleton):
    """ The Logger class is a singleton that provides access to a message
    logger.
    """

    @Singleton.instance.default
    def instance(self):
        """ Invoked to return the default logger. """

        from .stdout_logger import StdoutLogger

        return StdoutLogger()
