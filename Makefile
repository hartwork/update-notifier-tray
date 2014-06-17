.PHONY: dist
dist:
	./setup.py sdist

.PHONY: install
install:
	./setup.py install --prefix /usr --root "$(DESTDIR)"

.PHONY: deb
deb:
	debuild -us -uc
