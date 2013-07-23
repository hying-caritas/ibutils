all:build

build:
	./setup.py build

develop:
	./setup.py develop

undevelop:
	./setup.py develop -u

clean:
	rm -rf build *.egg-info dist
