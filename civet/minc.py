"""
Classes for working with volume (`.mnc`) files.
"""

from os import PathLike
from abc import ABC
import subprocess as sp
from civet.abstract_data import DataSource, DataOperation, DataFile


class MincMixin(DataSource, ABC):
    """
    Provides a subclass with MINC volume related functions.
    """
    preferred_suffix = '.mnc'

    def reshape_bbox(self) -> 'MincMixin':
        """
        Runs

        ```shell
        mincreshape -quiet -clobber $(mincbbox -mincreshape in.mnc) in.mnc out.mnc
        ```
        """
        return _MincBBoxReshapeOperation(self)


class _MincBBoxReshapeOperation(DataOperation, MincMixin):
    def run(self, input: str | PathLike, output: str | PathLike):
        cmd = [
            'mincreshape', '-quiet', '-clobber',
            *self._mincbbox(input), input, output
        ]
        sp.run(cmd, check=True)

    def _mincbbox(self, input: str | PathLike) -> list[str]:
        result = sp.check_output(['mincbbox', '-mincreshape', input])
        decoded = result.decode(encoding='utf-8')
        return decoded.split(' ')


class MincFile(DataFile, MincMixin):
    """
    Wraps a MINC (`.mnc`) file.

    Examples
    --------

    ```python
    from civet import MincFile

    MincFile('mask.mnc').reshape_bbox().save('bounded.mnc')
    ```
    """
    pass
