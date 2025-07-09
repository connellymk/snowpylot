Quickstart Guide
===============

This guide will help you get started with Snowpylot quickly. Here's a basic example of how to use the library:

Basic Usage
----------

To parse a CAAML file:

.. code-block:: python

   from snowpylot.caaml_parser import CAAMLParser

   # Initialize the parser
   parser = CAAMLParser()

   # Parse a CAAML file
   snowpit = parser.parse("path/to/your/snowpit.xml")

   # Access basic snowpit information
   print(f"Location: {snowpit.location}")
   print(f"Date: {snowpit.date}")
   print(f"Elevation: {snowpit.elevation}m")

Working with Snow Layers
-----------------------

To access and analyze snow layers:

.. code-block:: python

   # Get all snow layers
   layers = snowpit.layers

   # Access specific layer properties
   for layer in layers:
       print(f"Layer depth: {layer.depth}cm")
       print(f"Layer hardness: {layer.hardness}")
       print(f"Layer grain type: {layer.grain_type}")

Exporting Data
-------------

To export your snowpit data:

.. code-block:: python

   # Export to CSV
   snowpit.to_csv("snowpit_data.csv")

   # Export to JSON
   snowpit.to_json("snowpit_data.json")

For more detailed information about specific features, please refer to the :doc:`modules/parser` and :doc:`modules/whumpfdata` documentation.
