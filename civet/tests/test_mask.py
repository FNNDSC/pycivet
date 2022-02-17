import pytest
from pytest_mock import MockerFixture
from pathlib import Path
from civet.mask import Mask
from civet.tests.helpers import Intermediate, assert_save_chain, FINAL_OUTPUT
from typing import Sequence
from os import PathLike
import subprocess as sp


@pytest.fixture()
def tmp_mnc(tmp_path: Path) -> Path:
    mnc = tmp_path.with_suffix('.mnc')
    mnc.touch()
    return mnc


def test_bbox(mocker: MockerFixture, tmp_mnc: Path):
    mocker.patch('subprocess.check_output', return_value=b'a b c')
    expected = [
        mocker.call(['cp', Intermediate(0), Intermediate(1)]),
        mocker.call(['mincreshape', '-quiet', '-clobber', 'a', 'b', 'c', Intermediate(1), FINAL_OUTPUT])
    ]
    assert_save_chain(Mask(tmp_mnc).reshape_bbox(), expected)


def test_minccalc(tmp_mnc: Path):
    mask_paths = [tmp_mnc.with_stem(f'example_{i}') for i in range(3)]
    for i, m in enumerate(mask_paths):
        m.write_text(f'mask #{i + 1}')

    mask1, mask2, mask3 = map(Mask, mask_paths)

    has_minccalc = False

    def runner(cmd: Sequence[str | PathLike]):
        if cmd[0] != 'minccalc':
            sp.run(cmd, check=True)
            return

        nonlocal has_minccalc
        assert not has_minccalc, 'tried to run a second minccalc'
        has_minccalc = True

        assert cmd[0:7] == [
            'minccalc', '-clobber', '-quiet', '-unsigned', '-byte',
            '-expression', 'EXAMPLE_EXPRESSION'
        ]
        assert len(cmd[7:]) == 4, f'Command has wrong arguments: {cmd}'
        assert cmd[-1] == FINAL_OUTPUT
        int_mask1, int_mask2, int_mask3 = cmd[7:10]
        assert int_mask1.read_text() == 'mask #1'
        assert int_mask2.read_text() == 'mask #2'
        assert int_mask3.read_text() == 'mask #3'

    mask1.minccalc_u8('EXAMPLE_EXPRESSION', mask2, mask3)\
        .save(FINAL_OUTPUT, shell=runner, require_output=False)
    assert has_minccalc
