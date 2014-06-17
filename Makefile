.PHONY: dist
dist:
	./setup.py sdist

.PHONY: install
install:
	./setup.py install --prefix /usr --root "$(DESTDIR)"
	cd "$(DESTDIR)"/usr/lib/python*/ && mv site-packages dist-packages

.PHONY: deb
deb:
	debuild -us -uc
