"""
Classes related to pre- and post-processing for
`sphere_mesh` (the implementation of marching-cubes
in CIVET-2.1.1).
"""

from os import PathLike
from typing import Sequence, Optional
from civet.abstract_data import AbstractDataCommand
from civet.minc import Mask, GenericMask
from civet.extraction.starting_models import SurfaceModel, WHITE_MODEL_320
from civet.extraction.surfaces import IrregularSurface
from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    """
    Brain hemisphere side.
    """
    LEFT = 'left'
    RIGHT = 'right'


class HemisphereMask(GenericMask['HemisphereMask']):
    """
    Represents a binary mask of a brain hemisphere (either left or right).
    """

    def just_sphere_mesh(self, side: Optional[Side]) -> IrregularSurface:
        """
        Just run `sphere_mesh`, which produces a mesh with non-standard connectivity.
        """
        model = self.get_model_for(side)
        return self.prepare_for_sphere_mesh(model).sphere_mesh()

    def prepare_for_sphere_mesh(self, initial_model: SurfaceModel) -> 'SphereMeshMask':
        """
        Prepare this mask for `sphere_mesh`.

        https://github.com/aces/surface-extraction/blob/7c9c5987a2f8f5fdeb8d3fd15f2f9b636401d9a1/scripts/marching_cubes.pl.in#L189-L207

        Parameters
        ----------
        initial_model: SurfaceModel
            bounds
        """
        filled = self.minccalc_u8('out=1')
        surface_mask_vol = initial_model.surface_mask2(filled)
        resampled = surface_mask_vol.mincresample(filled)
        overlap = self.minccalc_u8('if(A[0]>0.5||A[1]>0.5){1}else{0}', resampled)
        dilated = overlap.dilate_volume(1, 26, 1)
        added = self.minccalc_u8('A[0]+A[1]', dilated)
        defragged = added.reshape255().mincdefrag(2, 19)
        return SphereMeshMask(defragged)

    @staticmethod
    def get_model_for(side: Optional[Side] = None) -> SurfaceModel:
        """
        Transform `WHITE_MODEL_320` as necessary in preparation for use with `sphere_mesh`.

        https://github.com/aces/surface-extraction/blob/7c9c5987a2f8f5fdeb8d3fd15f2f9b636401d9a1/scripts/marching_cubes.pl.in#L118-L135
        """
        initial_model = WHITE_MODEL_320
        if side is Side.LEFT:
            return initial_model.slide_left()
        elif side is Side.RIGHT:
            return initial_model.flip_x().slide_right()
        else:
            return initial_model


@dataclass(frozen=True)
class SphereMeshMask:
    """
    Represents a mask which is suitable input to the `sphere_mesh` program.
    """

    sphere_mesh_mask: Mask
    """
    `sphere_mesh` expects a `.mnc` where the actual brain hemisphere mask
    is labeled with `2`. The `2` region should be contained within an
    oval region labeled `1`, which is produced by running `surface_mask2`
    on a `SurfaceModel`.
    """

    def sphere_mesh(self) -> IrregularSurface:
        class SphereMeshSurface(IrregularSurface):
            def command(self, output: str | PathLike
                        ) -> Sequence[str | PathLike | AbstractDataCommand]:
                return 'sphere_mesh', self.input, output
        return SphereMeshSurface(self.sphere_mesh_mask)
