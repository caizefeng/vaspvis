import numpy as np
import pytest

from vaspvis.doscar import parse_doscar

HEAD = ["   2   2   1   0", "  0.1 0.2 0.3 0.4", "  1.0E-05", "  CAR", "  System"]
BLOCK_HEADER = "   10.00000000  -10.00000000   4   1.23456789   1.00000000"


def make_doscar(total, projected=(), trailing_blank=False, block_header=BLOCK_HEADER):
    lines = HEAD + [block_header] + ["  ".join(f"{v:.8E}" for v in row) for row in total]
    for block in projected:
        lines += [block_header] + ["  ".join(f"{v:.8E}" for v in row) for row in block]
    return "\n".join(lines) + "\n" + ("\n" if trailing_blank else "")


def test_total_only(tmp_path):
    total = np.round(np.random.default_rng(0).random((4, 3)), 6)
    path = tmp_path / "DOSCAR"
    path.write_text(make_doscar(total))
    result = parse_doscar(str(path))
    assert set(result) == {"total"}
    np.testing.assert_array_equal(result["total"], total)


def test_spin_polarized_with_projections(tmp_path):
    rng = np.random.default_rng(1)
    total = np.round(rng.random((4, 5)), 6)
    projected = np.round(rng.random((3, 4, 19)), 6)
    path = tmp_path / "DOSCAR"
    path.write_text(make_doscar(total, projected))
    result = parse_doscar(str(path))
    assert set(result) == {"total", "projected"}
    np.testing.assert_array_equal(result["total"], total)
    assert result["projected"].shape == (3, 4, 19)
    np.testing.assert_array_equal(result["projected"], projected)


def test_trailing_blank_line(tmp_path):
    rng = np.random.default_rng(2)
    total, projected = rng.random((4, 3)), rng.random((2, 4, 10))
    path = tmp_path / "DOSCAR"
    path.write_text(make_doscar(total, projected, trailing_blank=True))
    result = parse_doscar(str(path))
    assert result["projected"].shape == (2, 4, 10)


def test_errors(tmp_path):
    path = tmp_path / "DOSCAR"
    path.write_text("\n".join(HEAD[:3]) + "\n")
    with pytest.raises(ValueError):
        parse_doscar(str(path))
    with pytest.raises(FileNotFoundError):
        parse_doscar(str(tmp_path / "missing"))


def test_nedos_fused_with_emin(tmp_path):
    # VASP prints the header with 2F16.8, I5, 2F16.8: NEDOS >= 10000 runs into emin
    rng = np.random.default_rng(3)
    total, projected = np.round(rng.random((10000, 3)), 6), np.round(rng.random((2, 10000, 10)), 6)
    header = "      3.25790723    -47.5056123510000     -1.70054230      1.00000000"
    path = tmp_path / "DOSCAR"
    path.write_text(make_doscar(total, projected, block_header=header))
    result = parse_doscar(str(path))
    np.testing.assert_array_equal(result["total"], total)
    assert result["projected"].shape == (2, 10000, 10)
    np.testing.assert_array_equal(result["projected"], projected)


def test_bad_block_header_raises(tmp_path):
    path = tmp_path / "DOSCAR"
    for header in ["   10.0  -10.0  -1   1.2   1.0", "   10.0  -10.0   0   1.2   1.0", "   10.0  -10.0   1.2"]:
        path.write_text(make_doscar(np.zeros((4, 3)), block_header=header))
        with pytest.raises(ValueError):
            parse_doscar(str(path))
