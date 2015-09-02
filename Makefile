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


PYTHON3=python3.4
PYTHON2=python

.PHONY: build dist clean dist-clean

all: gui

gui:
	$(MAKE) -C metasip/api_editor/Designer all

build: gui VERSION
	$(PYTHON2) build.py changelog
	$(PYTHON3) setup.py sdist --formats=gztar,zip --force-manifest --dist-dir=.

install: gui VERSION
	$(PYTHON3) setup.py install

dist: dist-clean build

clean:
	rm -rf ChangeLog* VERSION MANIFEST build dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -depth -name __pycache__ -exec rm -rf {} \;
	$(MAKE) -C metasip/api_editor/Designer clean

dist-clean: clean
	rm -f *.tar.gz *.zip

VERSION:
	$(PYTHON2) build.py -o VERSION version
