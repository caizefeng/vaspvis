import numpy as np
import pytest

from vaspvis.doscar import parse_doscar

HEAD = ["   2   2   1   0", "  0.1 0.2 0.3 0.4", "  1.0E-05", "  CAR", "  System"]
BLOCK_HEADER = "   10.00000000  -10.00000000   4   1.23456789   1.00000000"


def make_doscar(total, projected=(), trailing_blank=False):
    lines = HEAD + [BLOCK_HEADER] + ["  ".join(f"{v:.8E}" for v in row) for row in total]
    for block in projected:
        lines += [BLOCK_HEADER] + ["  ".join(f"{v:.8E}" for v in row) for row in block]
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
