from civet.mask import Mask, GenericMask
from civet.extraction.surfaces import IrregularSurface
from civet.extraction.starting_models import WHITE_MODEL_320, SurfaceModel
from enum import Enum
from typing import TypeVar, Generic, Optional
import subprocess as sp
from contextlib import contextmanager


class Side(Enum):
    LEFT = 'left'
    RIGHT = 'right'


_M = TypeVar('_M', bound='GenericHemisphere')


class GenericHemisphere(GenericMask[_M], Generic[_M]):
    """
    Provides helper functions which operate on hemisphere masks (`.mnc` files).
    """

    def just_sphere_mesh(self, side: Optional[Side]) -> IrregularSurface:
        """
        Extract surface using `sphere_mesh` (marching-cubes).
        """
        # https://github.com/aces/surface-extraction/blob/7c9c5987a2f8f5fdeb8d3fd15f2f9b636401d9a1/scripts/marching_cubes.pl.in#L118-L135
        initial_model = WHITE_MODEL_320
        if side is Side.LEFT:
            sided_model = initial_model.slide_left()
        elif side is Side.RIGHT:
            sided_model = initial_model.flip_x().slide_right()
        else:
            sided_model = initial_model

        return self.sphere_mesh_from(sided_model)

    def sphere_mesh_from(self, initial_model: SurfaceModel) -> IrregularSurface:
        """
        Prepare mask for marching-cubes using given model surface as a starting point,
        and then execute `sphere_mesh`.
        """
        def run(mask_file, surface):
            with self.prepare_mask_for_sphere_mesh(Mask(mask_file), initial_model) as sphere_mask:
                sp.run(['sphere_mesh', sphere_mask, surface], check=True)

        # watch out: can't use something.append because we're changing file types,
        # attributes are not going to be copied automatically
        return IrregularSurface(
            self, run=run, require_output=self.require_output
        )

    @staticmethod
    @contextmanager
    def prepare_mask_for_sphere_mesh(mask: Mask, initial_model: SurfaceModel):
        """
        https://github.com/aces/surface-extraction/blob/7c9c5987a2f8f5fdeb8d3fd15f2f9b636401d9a1/scripts/marching_cubes.pl.in#L189-L207
        """
        with mask.minccalc_u8('out=1').as_intermediate() as filled_file:
            filled_vol = Mask(filled_file)
            with initial_model.surface_mask2(filled_vol).as_intermediate() as surface_mask_file:
                surface_mask_vol = Mask(surface_mask_file)
                resampled = surface_mask_vol.mincresample(filled_vol)
                overlap = mask.minccalc_u8('if(A[0]>0.5||A[1]>0.5){1}else{0}', resampled)
                dilated = overlap.dilate_volume(1, 26, 1)
                added = mask.minccalc_u8('A[0]+A[1]', dilated)
                with added.reshape255().mincdefrag(2, 19).as_intermediate() as sphere_mask:
                    yield sphere_mask


class HemisphereMask(GenericHemisphere['HemisphereMask']):
    """
    Wraps a `.mnc` file representing a binary mask for a brain hemisphere.
    """
    pass
