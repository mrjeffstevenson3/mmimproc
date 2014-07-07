# simple makefile to simplify repetetive build env management tasks under posix

# caution: testing won't work on windows, see README

PYTHON ?= python
NOSETESTS ?= nosetests

all: clean inplace test

clean-pyc:
	find . -name "*.pyc" | xargs rm -f

clean-so:
	find . -name "*.so" | xargs rm -f
	find . -name "*.pyd" | xargs rm -f

clean-build:
	rm -rf build

clean: clean-build clean-pyc clean-so

flake:
	@if command -v flake8 > /dev/null; then \
           echo "Running flake8"; \
		flake8 --count pylabs examples; \
           echo "Done."; \
	else \
           echo "flake8 not found, please install it!"; \
	fi;


in: inplace # just a shortcut
inplace:
	@$(PYTHON) setup.py build_ext -i

nosetests:
	rm -f .coverage
	@$(NOSETESTS) pylabs

test: clean nosetests flake

