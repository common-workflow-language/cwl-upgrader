=====================================================
Common workflow language standalone document upgrader
=====================================================

This is a standalone upgrader for Common Workflow Language documents from
version "draft-3" to "v1.0".

It does not check for correctness of the input document, for that one can use
the CWL reference implementation.

This is written and tested for Python 2.7, 3.4, and 3.5.

Install
-------

Installing the official package from PyPI::

  pip install cwl-upgrader

Or from source::

  git clone https://github.com/common-workflow-language/cwl-upgrader.git
  pip install ./cwl-upgrader/

  # or if you don't have pip installed
  cd cwl-upgrader && python setup.py install

Run on the command line
-----------------------

::

  cwl-upgrader path-to-cwl-document
