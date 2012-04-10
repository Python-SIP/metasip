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


import sys


class Logger:
    """ The Logger class implements the default logger, i.e. one that simply
    writes messages to stdout.
    """

    def log(self, message):
        """ Log a message by writing it to stdout.

        :param message:
            is the message.
        """

        sys.stdout.write('{0}\n'.format(message))
