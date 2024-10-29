# Create docs/source/index.rst
Welcome to Gallbladder Analysis Documentation
===========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   contributing
   changelog

Introduction
------------

The Gallbladder Analysis project is a comprehensive toolkit for analyzing gallbladder surgery data.
It includes components for data collection, processing, analysis, and visualization.

Quick Start
----------

Installation
^^^^^^^^^^^

.. code-block:: bash

   pip install gallbladder-analysis

Basic Usage
^^^^^^^^^^

.. code-block:: python

   from gallbladder_analysis import GallbladderAnalyzer

   analyzer = GallbladderAnalyzer()
   analyzer.run_analysis()

Features
--------

* Web scraping of medical data
* Data processing and cleaning
* Statistical analysis
* Interactive dashboard
* PDF report generation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`