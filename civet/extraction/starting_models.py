"""
Data from the `$MNI_DATAPATH/surface-extraction` directory.
"""
from pathlib import Path
from typing import Optional

from civet.extraction.surfaces import RegularSurface
from civet.globals import MNI_DATAPATH


class SurfaceModel(RegularSurface['SurfaceModel']):
    """
    Represents a surface data file from the `$MNI_DATAPATH/surface-extraction` directory.
    """
    @classmethod
    def get_model(cls, name: str) -> Optional['SurfaceModel']:
        data_paths = MNI_DATAPATH.split(':')
        possible_models = map(lambda b: Path(b) / 'surface-extraction' / name, data_paths)
        actual_model_paths = filter(lambda p: p.is_file(), possible_models)
        actual_models = map(cls, actual_model_paths)
        return next(actual_models, None)


WHITE_MODEL_320 = SurfaceModel.get_model('white_model_320.obj')
