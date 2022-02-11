"""
Surface model files. These are typically the starting point
for surface extraction algorithms.
"""

from os import PathLike
from civet.globals import MNI_DATAPATH
from civet.extraction.surfaces import GenericRegularSurface


class SurfaceModel(GenericRegularSurface['SurfaceModel']):

    @classmethod
    def get_model(cls, name: str | PathLike) -> 'SurfaceModel':
        return cls(MNI_DATAPATH / 'surface-extraction' / name)


WHITE_MODEL_320 = SurfaceModel.get_model('white_model_320.obj')
