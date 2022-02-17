import pytest
from pytest_mock import MockerFixture
from unittest.mock import call, MagicMock, ANY
from civet.obj import Surface
from pathlib import Path


@pytest.fixture()
def tmp_obj(tmp_path: Path) -> Path:
    obj = tmp_path.with_suffix('.obj')
    obj.touch()
    return obj


@pytest.fixture()
def surf(tmp_obj: Path) -> Surface:
    return Surface(tmp_obj)


@pytest.fixture()
def mock_run(mocker: MockerFixture):
    return mocker.patch('subprocess.run')


def test_slide_left(mock_run: MagicMock, surf: Surface):
    surf.slide_left().save('result.obj')
    mock_run.assert_has_calls([
        call(['param2xfm', '-clobber', '-translation', '-25', '0', '0', ANY], check=True),
        call(['transform_objects', ANY, ANY, 'result.obj'], check=True)
    ])


def test_slide_right(mock_run: MagicMock, surf: Surface):
    surf.slide_right().save('result.obj')
    mock_run.assert_has_calls([
        call(['param2xfm', '-clobber', '-translation', '25', '0', '0', ANY], check=True),
        call(['transform_objects', ANY, ANY, 'result.obj'], check=True)
    ])


def test_flip(mock_run: MagicMock, surf: Surface):
    surf.flip_x().save('result.obj')
    mock_run.assert_has_calls([
        call(['param2xfm', '-clobber', '-scales', '-1', '1', '1', ANY], check=True),
        call(['transform_objects', ANY, ANY, 'result.obj'], check=True)
    ])


def _get_last_arg(call_args: tuple[tuple[str, ...], tuple]):
    return call_args[0][0][-1]


def test_flip_and_slide(mock_run: MagicMock, surf: Surface):
    surf.flip_x().slide_right().save('result.obj')
    assert mock_run.mock_calls[0] == call(['param2xfm', '-clobber', '-scales', '-1', '1', '1', ANY], check=True)
    flip_xfm = _get_last_arg(mock_run.call_args_list[0])
    assert mock_run.mock_calls[1] == call(['transform_objects', ANY, flip_xfm, ANY], check=True)
    flipped_obj = _get_last_arg(mock_run.call_args_list[1])
    assert mock_run.mock_calls[2] == call(['param2xfm', '-clobber', '-translation', '25', '0', '0', ANY], check=True)
    slide_xfm = _get_last_arg(mock_run.call_args_list[2])
    assert mock_run.mock_calls[3] == call(['transform_objects', flipped_obj, slide_xfm, 'result.obj'], check=True)
