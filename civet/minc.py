"""
Defines types and operations related to MINC files.
"""
from civet.bases import DataFile
from typing import Literal, TypeVar, Generic, Optional
from dataclasses import dataclass

_M = TypeVar('_M', bound='Mask')


@dataclass(frozen=True)
class GenericMask(DataFile[_M], Generic[_M]):

    preferred_suffix = '.mnc'

    def dilate_volume(self, dilation_value: int, neighbors: Literal[6, 26], n_dilations: int) -> 'Mask':
        def command(output):
            return (
                'dilate_volume', self, output,
                str(dilation_value), str(neighbors), str(n_dilations)
            )
        return self.create_command(command)

    def mincresample(self, like_volume: _M) -> _M:
        def command(output):
            return (
                'mincresample', '-clobber', '-quiet',
                '-like', like_volume, self, output
            )
        return like_volume.create_command(command)

    def minccalc_u8(self, expression: str, *other_volumes: 'Mask') -> 'Mask':
        def command(output):
            return (
                'minccalc', '-clobber', '-quiet',
                '-unsigned', '-byte',
                '-expression', expression,
                self, *other_volumes, output
            )
        return self.create_command(command)

    def mincdefrag(self, label: int, stencil: Literal[6, 19, 27], max_connect: Optional[int] = None) -> _M:
        def command(output):
            cmd = ['mincdefrag', self, output, str(label), str(stencil)]
            if max_connect is not None:
                cmd.append(str(max_connect))
            return cmd
        return self.create_command(command)

    def mincblur(self, fwhm: int) -> _M:
        # reult is not a binary mask, it has float values in [0, 1],
        # maybe define a unique type?
        def command(output):
            return ('mincblur', '-fwhm', str(fwhm), self, output)
        return self.create_command(command)

    def reshape255(self) -> _M:
        def command(output):
            return (
                'mincreshape', '-quiet', '-clobber', '-unsigned', '-byte',
                '-image_range', '0', '255', '-valid_range', '0', '255',
                self, output
            )
        return self.create_command(command)

    def reshape_bbox(self) -> _M:
        def command(output):
            return 'mincreshape_bbox_helper', self, output
        return self.create_command(command)


class Mask(GenericMask['Mask']):
    """
    A `Mask` represents a volume (`.mnc`) with discrete intensities (segmentation volume or brain mask).
    """
    pass
