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


""" This module contains the implementation of the Qt5 :term:`toolkit`. """


from PyQt5.QtCore import PYQT_VERSION

# We require a version with sip.wrappertype as the meta-class.
if PYQT_VERSION < 0x050701:
    raise ValueError("PyQt v5.7.1 or later is required")


from .toolkit import Toolkit

# Register all the adapters.
from . import adapters
