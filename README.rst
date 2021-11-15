=====================================================
Common workflow language standalone document upgrader
=====================================================

This is a standalone upgrader for Common Workflow Language documents from
version ``draft-3``, ``v1.0``, and ``v1.1`` to ``v1.2``.

See https://github.com/sbg/sevenbridges-cwl-draft2-upgrader for upgrading from ``sbg:draft-2``.

It does not check for correctness of the input document, for that one can use
`the CWL reference implementation <https://github.com/common-workflow-language/cwltool>`_ (``cwltool --validate``).

This is written and tested for Python 3.6, 3.7, 3.8, 3.9, and 3.10.

Install
-------

Installing the official package from PyPI::

  pip install cwl-upgrader

Or from source::

  git clone https://github.com/common-workflow-language/cwl-upgrader.git
  pip install ./cwl-upgrader/

Run on the command line
-----------------------

::

  cwl-upgrader path-to-cwl-document [another-path-to-cwl-document ...]
