import pytest
from unittest.mock import patch, call, MagicMock, ANY
from civet.surface import ObjFile
from pathlib import Path


@pytest.fixture()
def tmp_obj(tmp_path: Path) -> Path:
    obj = tmp_path.with_suffix('.obj')
    obj.touch()
    return obj


@patch('subprocess.run')
def test_slide_left(run: MagicMock, tmp_obj: Path):
    ObjFile(tmp_obj).slide_left().save('result.obj')

    run.assert_has_calls([
        call(['param2xfm', '-clobber', '-translation', '-25', '0', '0', ANY], check=True),
        call(['transform_objects', ANY, ANY, 'result.obj'], check=True)
    ])


@patch('subprocess.run')
def test_slide_right(run: MagicMock, tmp_obj: Path):
    ObjFile(tmp_obj).slide_right().save('result.obj')

    run.assert_has_calls([
        call(['param2xfm', '-clobber', '-translation', '25', '0', '0', ANY], check=True),
        call(['transform_objects', ANY, ANY, 'result.obj'], check=True)
    ])


@patch('subprocess.run')
def test_flip(run: MagicMock, tmp_obj: Path):
    ObjFile(tmp_obj).flip_x().save('result.obj')

    run.assert_has_calls([
        call(['param2xfm', '-clobber', '-scales', '-1', '1', '1', ANY], check=True),
        call(['transform_objects', ANY, ANY, 'result.obj'], check=True)
    ])


def _get_last_arg(call_args: tuple[tuple[str, ...], tuple]):
    return call_args[0][0][-1]


@patch('subprocess.run')
def test_flip_and_slide(run: MagicMock, tmp_obj: Path):
    ObjFile(tmp_obj).flip_x().slide_right().save('result.obj')
    assert run.mock_calls[0] == call(['param2xfm', '-clobber', '-scales', '-1', '1', '1', ANY], check=True)
    flip_xfm = _get_last_arg(run.call_args_list[0])
    assert run.mock_calls[1] == call(['transform_objects', ANY, flip_xfm, ANY], check=True)
    flipped_obj = _get_last_arg(run.call_args_list[1])
    assert run.mock_calls[2] == call(['param2xfm', '-clobber', '-translation', '25', '0', '0', ANY], check=True)
    slide_xfm = _get_last_arg(run.call_args_list[2])
    assert run.mock_calls[3] == call(['transform_objects', flipped_obj, slide_xfm, 'result.obj'], check=True)
