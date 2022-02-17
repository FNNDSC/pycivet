"""
Classes for working with mask volume (`.mnc`) files.

Examples
--------

```python
from civet.mask import Mask

Mask('wm.mnc').reshape_bbox().save('bounded.wm.mnc')
```
"""

from pathlib import Path
from os import PathLike
from dataclasses import dataclass
import subprocess as sp
from civet.abstract_data import DataSource
from typing import TypeVar, Generic, Literal, Optional


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
        def run(inputs: tuple[Path], output: str) -> list[str | PathLike]:
            vol, = inputs
            return [
                'mincreshape', '-quiet', '-clobber',
                *self._mincbbox(vol), vol, output
            ]

        return self.append(run)

    @staticmethod
    def _mincbbox(input: PathLike) -> list[str]:
        result = sp.check_output(['mincbbox', '-mincreshape', input])
        decoded = result.decode(encoding='utf-8')
        return decoded.split(' ')

    def minccalc_u8(self, expression: str, *args: _O) -> _M:
        """
        Runs

        ```shell
        minccalc -quiet -unsigned -byte -expression ... inputs ...
        ```

        Examples
        --------

        ```python
        MaskFile('one.mnc').minccalc_u8('A[0]+A[1]', MaskFile('two.mnc')).save('overlap.mnc')
        ```
        """
        def run(inputs: tuple[Path, ...], output: str) -> list[str | PathLike]:
            return [
                'minccalc', '-clobber', '-quiet',
                '-unsigned', '-byte',
                '-expression', expression,
                *inputs, output
            ]
        return self.append_join(run, (self, *args))

    def mincresample(self, like: _O) -> _O:
        def run(inputs: tuple[Path, Path], output_file: str) -> list[str | PathLike]:
            input_file, like_volume = inputs
            return [
                'mincresample', '-clobber', '-quiet',
                '-like', like_volume,
                input_file, output_file
            ]
        return like.append(run)

    def dilate_volume(self, dilation_value: int, neighbors: Literal[6, 26], n_dilations: int) -> _M:
        def run(inputs: tuple[Path], output: str) -> list[str | PathLike]:
            return [
                'dilate_volume', inputs[0], output,
                str(dilation_value), str(neighbors), str(n_dilations)
            ]
        return self.append(run)

    def reshape255(self) -> _M:
        def run(inputs: tuple[Path], output: str) -> list[str | PathLike]:
            return [
                'mincreshape', '-quiet', '-clobber', '-unsigned', '-byte',
                '-image_range', '0', '255', '-valid_range', '0', '255',
                inputs[0], output
            ]
        return self.append(run)

    def mincdefrag(self, label: int, stencil: Literal[6, 19, 27], max_connect: Optional[int] = None) -> _M:
        def run(inputs: tuple[Path], output: str) -> list[str | PathLike]:
            cmd = ['mincdefrag', inputs[0], output, str(label), str(stencil)]
            if max_connect is not None:
                cmd.append(str(max_connect))
            return cmd
        return self.append(run)


class Mask(GenericMask['Mask']):
    """
    Wraps a MINC (`.mnc`) file.

    Examples
    --------

    ```python
    from civet import MaskFile

    MaskFile('mask.mnc').reshape_bbox().save('bounded.mnc')
    MaskFile('one.mnc').minccalc_u8('A[0]||A[1]', MaskFile('two.mnc')).save('union.mnc')
    ```
    """
    pass
