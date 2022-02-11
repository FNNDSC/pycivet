import pytest
from pytest_mock import MockerFixture
from pathlib import Path
from unittest.mock import ANY
from civet.mask import Mask


@pytest.fixture()
def tmp_mnc(tmp_path: Path) -> Path:
    mnc = tmp_path.with_suffix('.mnc')
    mnc.touch()
    return mnc


def test_bbox(mocker: MockerFixture, tmp_mnc: Path):
    mock_copyfile = mocker.patch('shutil.copyfile')
    mock_run = mocker.patch('subprocess.run')
    mock_check_output = mocker.patch('subprocess.check_output', return_value=b'a b c')

    mask = Mask(tmp_mnc, require_output=False)

    # spy_first_run = mocker.spy(mask, 'run')
    # https://github.com/pytest-dev/pytest-mock/issues/280
    spy_first_run = mocker.MagicMock(wraps=mask.run)
    object.__setattr__(mask, 'run', spy_first_run)
    mask.reshape_bbox().save('bounded.mnc')

    mock_copyfile.assert_called_once_with(tmp_mnc, ANY)
    _, copied_to_tmp = mock_copyfile.call_args[0]
    spy_first_run.assert_called_once_with(copied_to_tmp, ANY)
    _, copied_mnc = spy_first_run.call_args[0]
    assert copied_mnc.endswith('.mnc')

    mock_check_output.assert_called_once_with(['mincbbox', '-mincreshape', copied_mnc])
    expected = ['mincreshape', '-quiet', '-clobber', 'a', 'b', 'c', copied_mnc, 'bounded.mnc']
    mock_run.assert_called_once_with(expected, check=True)
