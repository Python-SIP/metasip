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


FORMS = \
	MainWindowBase.py \
	ArgPropertiesBase.py \
	CallablePropertiesBase.py \
	ClassPropertiesBase.py \
	OpaqueClassPropertiesBase.py \
	VariablePropertiesBase.py \
	EnumPropertiesBase.py \
	EnumValuePropertiesBase.py \
	HeaderDirectoryPropertiesBase.py \
	ModulePropertiesBase.py \
	ProjectPropertiesBase.py \
	PlatformPickerBase.py \
	FeaturePickerBase.py \
	ManualCodeBase.py \
	GenerationsBase.py


all: $(FORMS)

clean:
	rm -rf $(FORMS) *.ui~ *.pyc *.pyo


# Tell make how to create the Python files.
.SUFFIXES: .py .ui

.ui.py:
	pyuic4 -o $@ $<
