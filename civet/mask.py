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
from typing import TypeVar, Generic, ContextManager, Literal, Optional
from contextlib import ExitStack


_M = TypeVar('_M', bound='GenericMask')
_O = TypeVar('_O', bound='GenericMask')


@dataclass(frozen=True)
class GenericMask(DataSource[_M], Generic[_M]):
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

    def minccalc_u8(self, expression: str, *args: _O) -> _M:
        def run(input, output):
            others: list[ContextManager[str | PathLike]] = [other.intermediate_saved() for other in args]
            with ExitStack() as stack:
                other_files = (stack.enter_context(o) for o in others)
                cmd = [
                    'minccalc', '-clobber', '-quiet',
                    '-unsigned', '-byte',
                    '-expression', expression,
                    input, *other_files, output
                ]
                sp.run(cmd, check=True)

        return self.append(run)

    def mincresample(self, like: _O) -> _O:
        def run(like_volume, output_file):
            with self.intermediate_saved() as input_file:
                cmd = [
                    'mincresample', '-clobber', '-quiet',
                    '-like', like_volume,
                    input_file, output_file
                ]
                sp.run(cmd, check=True)

        return like.append(run)

    def dilate_volume(self, dilation_value: int, neighbors: Literal[6, 26], n_dilations: int) -> _M:
        def run(input, output):
            cmd = ['dilate_volume', input, output, str(dilation_value), str(neighbors), str(n_dilations)]
            sp.run(cmd, check=True)
        return self.append(run)

    def reshape255(self) -> _M:
        def run(input, output):
            cmd = [
                'mincreshape', '-quiet', '-clobber', '-unsigned', '-byte',
                '-image_range', '0', '255', '-valid_range', '0', '255',
                input, output
            ]
            sp.run(cmd, check=True)
        return self.append(run)

    def mincdefrag(self, label: int, stencil: Literal[6, 19, 27], max_connect: Optional[int] = None) -> _M:
        def run(input, output):
            cmd = ['mincdefrag', input, output, str(label), str(stencil)]
            if max_connect is not None:
                cmd.append(str(max_connect))
            sp.run(cmd, check=True)
        return self.append(run)


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
