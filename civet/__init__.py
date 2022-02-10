"""
Object-oriented Python bindings for CIVET binaries such as
`transform_objects` and `mincreshape`.
"""

import civet.minc as minc
# from civet.minc import MincFile, MincMixin
# from civet.surface import ObjFile, HemisphereMixin
import civet.surface as surface
# from civet.abstract_data import DataSource, DataFile
import civet.abstract_data as abstract_data

import os
from pathlib import Path

__fallback_path = '/runtime/path/to/CIVET/quarantines/Linux-x86_64/share'
MNI_DATAPATH = Path(os.getenv('MNI_DATAPATH', __fallback_path))
"""
Location of data such as starting ellipsoids for surface extraction.
"""

__docformat__ = 'numpy'

__all__ = [
    'MNI_DATAPATH',
    'minc',
    # 'MincFile',
    # 'MincMixin',
    # 'ObjFile',
    # 'HemisphereMixin',
    'surface',
    # 'DataFile',
    # 'DataSource'
    'abstract_data'
]
