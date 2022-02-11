"""
Classes for working with mask volume (`.mnc`) files.

Examples
--------

```python
from civet.mask import Mask

Mask('wm.mnc').reshape_bbox().save('bounded.wm.mnc')
```
"""

from os import PathLike
from dataclasses import dataclass
import subprocess as sp
from civet.abstract_data import DataSource
from typing import TypeVar, Generic

_M = TypeVar('_M', bound='GenericMask')


@dataclass(frozen=True)
class GenericMask(DataSource, Generic[_M]):
    """
    Provides a subclass with MINC volume mask related functions.
    """
    preferred_suffix = '.mnc'

    def reshape_bbox(self) -> _M:
        """
        Runs

        ```shell
        mincreshape -quiet -clobber $(mincbbox -mincreshape in.mnc) in.mnc out.mnc
        ```
        """
        def run(input: str | PathLike, output: str | PathLike) -> None:
            cmd = [
                'mincreshape', '-quiet', '-clobber',
                *self._mincbbox(input), input, output
            ]
            sp.run(cmd, check=True)

        return self.append(run)

    @staticmethod
    def _mincbbox(input: str | PathLike) -> list[str]:
        result = sp.check_output(['mincbbox', '-mincreshape', input])
        decoded = result.decode(encoding='utf-8')
        return decoded.split(' ')


class Mask(GenericMask['Mask']):
    """
    Wraps a MINC (`.mnc`) file.

    Examples
    --------

    ```python
    from civet import MaskFile

    MaskFile('mask.mnc').reshape_bbox().save('bounded.mnc')
    ```
    """
    pass
