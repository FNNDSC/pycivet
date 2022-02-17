# pycivet

[![.github/workflows/test.yml](https://github.com/FNNDSC/pycivet/actions/workflows/test.yml/badge.svg)](https://github.com/FNNDSC/pycivet/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/pycivet)](https://pypi.org/project/pycivet/)
[![License - MIT](https://img.shields.io/pypi/l/pycivet)](https://github.com/FNNDSC/pycivet/blob/master/LICENSE)

Object-oriented Python bindings for CIVET binaries like `transform_objects` and `mincreshape`.

## Abstract

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

## Motivation

Typically, bioinformatics and neuroinformatics pipelines such as
[CIVET](https://www.bic.mni.mcgill.ca/ServicesSoftware/CIVET-2-1-0-Table-of-Contents)
and [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/) are comprised of
many binary programs and a script in `csh` or `perl` which glues together
those binary programs and their intermediate results. These scripts usually
look like:

```shell
do_something input.mnc /tmp/1.mnc
another_thing /tmp/1.mnc /tmp/2.mnc
create_thing /tmp/3.mnc
many_thing /tmp/2.mnc /tmp/3.mnc /tmp/4.mnc
...
```

We propose that the readability and maintainability of such scripts can be
improved using modern programming language features such as type hints.
These advantages would enable to faster development and with fewer bugs.
`pycivet` demonstrates this claim with tools from CIVET.

### Intermediate Files

Consider this excerpt from `marching_cubes.pl`:

```perl
&run( "param2xfm", "-scales", -1, 1, 1,
    "${tmpdir}/flip.xfm" );
&run( "transform_objects", $ICBM_white_model,
    "${tmpdir}/flip.xfm", $initial_model );
unlink( "${tmpdir}/flip.xfm" );
&run( "param2xfm", "-translation", 25, 0, 0,
    "${tmpdir}/slide_right.xfm" );
&run( "transform_objects", $initial_model,
    "${tmpdir}/slide_right.xfm", $initial_model );
unlink( "${tmpdir}/slide_right.xfm" );
```

Using `pycivet` we can express the code more concisely:

```python
Surface('input.obj').flip_x().translate_x(25).save('./output.obj')
```

To the developer and code reviewer, management of a temporary space for
intermediate files happens transparently and behind-the-scenes.

### Typing

Only methods relevant to an object's type are available to be called on
that object. For instance, an object representing a `.obj` surface file
would have the methods `flip_x()` and `translate_x(n)`, and an object
representing a `.mnc` volume would have the methods `minccalc_u8(...)`
and `mincresample(...)` defined, but you cannot call `mincresample(...)`
on the `.obj` object.

TODO example

## Scope

The syntax provides for a concise way to do scripting with some of
CIVET's subroutines. This framework can be extended to support
memoization for efficiency. (Memoization is not currently implemented
so it is necessary to use `with data_source.intermediate_source()`
to reuse an intermediate output more than once without recomputing it.)
