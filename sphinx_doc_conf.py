# Create docs/source/conf.py
# Configuration file for the Sphinx documentation builder
project = 'Gallbladder Analysis'
copyright = '2024, SDWYates'
author = 'Your Name'
release = '1.0.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme',
]

# Theme
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
templates_path = ['_templates']

# Other settings
exclude_patterns = []
language = 'en'
