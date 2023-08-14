# This file is part of cwl-upgrader
# https://github.com/common-workflow-language/cwl-upgrader/, and is
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Contact: common-workflow-language@googlegroups.com

# make format to fix most python formatting errors
# make pylint to check Python code for enhanced compliance including naming
#  and documentation
# make coverage-report to check coverage of the python scripts by the tests

MODULE=cwl-upgrader
PACKAGE=cwlupgrader
EXTRAS=

# `SHELL=bash` doesn't work for some, so don't use BASH-isms like
# `[[` conditional expressions.
PYSOURCES=$(wildcard cwlupgrader/**.py tests/*.py) setup.py
DEVPKGS=diff_cover black pylint pep257 pydocstyle flake8 tox tox-pyenv \
	isort wheel autoflake flake8-bugbear pyupgrade bandit build \
	auto-walrus -rtest-requirements.txt -rmypy-requirements.txt
DEBDEVPKGS=pylint python3-coverage sloccount \
	   python3-flake8 shellcheck
VERSION=2.0.0  # please also update setup.py

## all                    : default task (install cwl-upgrader in dev mode)
all: dev

## help                   : print this help message and exit
help: Makefile
	@sed -n 's/^##//p' $<

## cleanup                : shortcut for "make sort_imports format flake8 diff_pydocstyle_report"
cleanup: sort_imports format flake8 diff_pydocstyle_report

## install-dep            : install most of the development dependencies via pip
install-dep: install-dependencies

install-dependencies: FORCE
	pip install --upgrade $(DEVPKGS)
	pip install -r requirements.txt -r mypy-requirements.txt

## install                : install the cwlupgrader package and scripts
install: FORCE
	pip install .$(EXTRAS)

## dev                    : install the cwlupgrader package in dev mode
dev: install-dep
	pip install -U pip setuptools wheel
	pip install -e .$(EXTRAS)

## dist                   : create a module package for distribution
dist: dist/${MODULE}-$(VERSION).tar.gz

dist/${MODULE}-$(VERSION).tar.gz: $(SOURCES)
	python -m build

## clean                  : clean up all temporary / machine-generated files
clean: FORCE
	rm -f ${MODILE}/*.pyc tests/*.pyc
	python setup.py clean --all || true
	rm -Rf .coverage
	rm -f diff-cover.html

# Linting and code style related targets
## sort_import            : sorting imports using isort: https://github.com/timothycrosley/isort
sort_imports: $(PYSOURCES) mypy-stubs
	isort $^

remove_unused_imports: $(PYSOURCES)
	autoflake --in-place --remove-all-unused-imports $^

pep257: pydocstyle
## pydocstyle             : check Python docstring style
pydocstyle: $(PYSOURCES)
	pydocstyle --add-ignore=D100,D101,D102,D103 $^ || true

pydocstyle_report.txt: $(PYSOURCES)
	pydocstyle setup.py $^ > $@ 2>&1 || true

## diff_pydocstyle_report : check Python docstring style for changed files only
diff_pydocstyle_report: pydocstyle_report.txt
	diff-quality --compare-branch=main --violations=pydocstyle --fail-under=100 $^

## codespell              : check for common misspellings
codespell:
	codespell -w $(shell git ls-files | grep -v mypy-stubs | grep -v gitignore | grep -v EDAM.owl | grep -v pre.yml | grep -v test_schema)

## format                 : check/fix all code indentation and formatting (runs black)
format:
	black setup.py cwlupgrader tests mypy-stubs

format-check:
	black --diff --check cwlupgrader setup.py mypy-stubs

## pylint                 : run static code analysis on Python code
pylint: $(PYSOURCES)
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
                $^ -j0|| true

pylint_report.txt: $(PYSOURCES)
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
		$^ -j0> $@ || true

diff_pylint_report: pylint_report.txt
	diff-quality --compare-branch=main --violations=pylint pylint_report.txt

.coverage: testcov

coverage: .coverage
	coverage report

coverage.xml: .coverage
	coverage xml

coverage.html: htmlcov/index.html

htmlcov/index.html: .coverage
	coverage html
	@echo Test coverage of the Python code is now in htmlcov/index.html

coverage-report: .coverage
	coverage report

diff-cover: coverage.xml
	diff-cover --compare-branch=main $^

diff-cover.html: coverage.xml
	diff-cover --compare-branch=main $^ --html-report $@

## test                   : run the cwlupgrader test suite
test: $(PYSOURCES)
	python -m pytest -rs ${PYTEST_EXTRA}

## testcov                : run the cwlupgrader test suite and collect coverage
testcov: $(PYSOURCES)
	python setup.py test --addopts "--cov" ${PYTEST_EXTRA}

sloccount.sc: $(PYSOURCES) Makefile
	sloccount --duplicates --wide --details $^ > $@

## sloccount              : count lines of code
sloccount: $(PYSOURCES) Makefile
	sloccount $^

list-author-emails:
	@echo 'name, E-Mail Address'
	@git log --format='%aN,%aE' | sort -u | grep -v 'root'

mypy3: mypy
mypy: $(PYSOURCES)
	MYPYPATH=$$MYPYPATH:mypy-stubs mypy $^

shellcheck: FORCE
	shellcheck conformance-test.sh release-test.sh

pyupgrade: $(PYSOURCES)
	pyupgrade --exit-zero-even-if-changed --py38-plus $^
	auto-walrus $^

release-test: FORCE
	git diff-index --quiet HEAD -- || ( echo You have uncommitted changes, please commit them and try again; false )
	./release-test.sh

release: release-test
	. testenv2/bin/activate && \
		python testenv2/src/${MODULE}/setup.py sdist bdist_wheel && \
		pip install twine && \
		twine upload testenv2/src/${MODULE}/dist/* && \
		git tag v${VERSION} && git push --tags

flake8: FORCE
	flake8 $(PYSOURCES)

FORCE:

# Use this to print the value of a Makefile variable
# Example `make print-VERSION`
# From https://www.cmcrossroads.com/article/printing-value-makefile-variable
print-%  : ; @echo $* = $($*)
