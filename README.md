Python client for Basepair
======================

Python bindings for Basepair's API and command line interface (CLI).

## How to build and push to pypi:

```BASH
python setup.py sdist bdist_wheel # This will create two files in a newly created dist directory, a source archive and a wheel:
twine upload dist/* # To upload it to Pypi
```
