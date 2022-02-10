# pycivet

[![.github/workflows/test.yml](https://github.com/FNNDSC/pycivet/actions/workflows/test.yml/badge.svg)](https://github.com/FNNDSC/pycivet/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/pycivet)](https://pypi.org/project/pycivet/)
[![License - MIT](https://img.shields.io/pypi/l/pycivet)](https://github.com/FNNDSC/pycivet/blob/master/LICENSE)

Object-oriented Python bindings for CIVET binaries like `transform_objects` and `mincreshape`.

## Overview

`pycivet` provides helper methods which lazily invoke CIVET binaries with object-oriented syntax.
Intermediate files are written to temporary locations and then unlinked immediately.

This Perl code snippet from `marching_cubes.pl` can be expressed in Python as such:

https://github.com/aces/surface-extraction/blob/7c9c5987a2f8f5fdeb8d3fd15f2f9b636401d9a1/scripts/marching_cubes.pl.in#L125-L134

```python
from civet import MNI_DATAPATH
from civet.surface import ObjFile

starting_model = ObjFile(MNI_DATAPATH / 'surface-extraction' / 'white_model_320.obj')
starting_model.flip_x().slide_right().save('./output.obj')
```

## Installation

It is recommended you install this package in a container image, e.g.

```Dockerfile
FROM docker.io/fnndsc/mni-conda-base:civet2.1.1-python3.10.2
RUN pip install pycivet
```
