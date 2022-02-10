import pytest
from os import PathLike
from pathlib import Path
from unittest.mock import patch, Mock, ANY
from civet.minc import MincFile
from civet.abstract_data import DataOperation


@pytest.fixture()
def tmp_mnc(tmp_path: Path) -> Path:
    mnc = tmp_path.with_suffix('.mnc')
    mnc.touch()
    return mnc


@patch('subprocess.check_output', return_value=b'a b c')
@patch('subprocess.run')
@patch('shutil.copyfile')
def test_bbox(copyfile: Mock, sp_run: Mock, check_output: Mock, tmp_mnc: Path):
    MincFile(tmp_mnc).reshape_bbox().save('bounded.mnc')

    copyfile.assert_called_once_with(tmp_mnc, ANY)
    _, copied_mnc = copyfile.call_args[0]

    check_output.assert_called_once_with(['mincbbox', '-mincreshape', copied_mnc])
    expected = ['mincreshape', '-quiet', '-clobber', 'a', 'b', 'c', copied_mnc, 'bounded.mnc']
    sp_run.assert_called_once_with(expected, check=True)
