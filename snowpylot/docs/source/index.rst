.. snowpylot documentation master file, created by
   sphinx-quickstart on Fri Mar 14 08:15:05 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Snowpylot's documentation!
=====================================

Snowpylot is a Python library for working with CAAML.XML files from SnowPilot. This documentation will help you understand how to use the library effectively.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started:

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   modules/parser
   modules/whumpfdata
   modules/coreinfo
   modules/layer
   modules/snowprofile
   modules/stabilitytests

API Reference
-------------

.. autosummary::
   :toctree: _autosummary
   :recursive:

   snowpylot.caaml_parser
   snowpylot.coreInfo
   snowpylot.whumpfData
   snowpylot.layer
   snowpylot.snowProfile
   snowpylot.stabilityTests

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
