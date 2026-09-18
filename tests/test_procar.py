import gzip
import os

import numpy as np
import pytest

from vaspvis.procar import parse_procar, repair_procar

HEADER = "ion      s     py     pz     px    dxy    dyz    dz2    dxz  x2-y2    tot"
HEADER_LORBIT10 = "ion      s      p      d    tot"


def _row(label, values):
    """Format one projection row; also return the numbers it will parse to."""
    tot = sum(values)
    lab = f"{label:5d}" if isinstance(label, int) else f"{label:<5s}"
    text = lab + "".join(f"{v:7.3f}" for v in values) + f"{tot:7.3f}"
    parsed = [0 if label == "tot" else label] + [float(f"{v:.3f}") for v in values] + [float(f"{tot:.3f}")]
    return text, parsed


def make_procar(data, header=HEADER, nions=None, tot_row=True, phase=False, blank_between=False):
    """Build PROCAR text from ``data[spin][k][band][component][ion] -> values``.

    Returns the text and the array pyprocar would have produced for it.
    """
    nspin, nk, nb = len(data), len(data[0]), len(data[0][0])
    ncomp = len(data[0][0][0])
    nions = nions or len(data[0][0][0][0])
    meta = f"# of k-points:  {nk:3d}         # of bands:  {nb:3d}         # of ions:  {nions:3d}"
    lines = ["PROCAR lm decomposed"]
    expected = []
    for s in range(nspin):
        lines += ([" ", meta] if s else [meta])
        for k in range(nk):
            lines += ["", f" k-point {k + 1:5d} :    0.00000000 0.{k:08d} 0.00000000     weight = 0.50000000", ""]
            for b in range(nb):
                lines += [f"band {b + 1:5d} # energy {-5.0 + b:12.8f} # occ.  1.00000000", " ", header]
                block = []
                for comp in range(ncomp):
                    rows = []
                    for i, values in enumerate(data[s][k][b][comp]):
                        text, exp = _row(i + 1, values)
                        lines.append(text)
                        rows.append(exp)
                    if tot_row:
                        text, exp = _row("tot", list(np.sum(data[s][k][b][comp], axis=0)))
                        lines.append(text)
                        if nions > 1:
                            rows.append(exp)
                    if blank_between:  # VASP 6 separates the blocks with a blank line
                        lines.append("")
                    block.append(rows)
                if phase:  # LORBIT = 12 phase factors: header without "tot", then "charge"
                    lines.append(header.rsplit(None, 1)[0])
                    for i in range(nions):
                        lines.append(f"{i + 1:5d}" + "".join(f"{0.1 * j:7.3f}" for j in range(2 * (len(header.split()) - 2))))
                    lines.append("charge" + "".join(f"{0.2:7.3f}" for _ in range(len(header.split()) - 1)))
                lines.append(" ")
                expected.append(block)
    # columns: ion index, one per orbital, total -> as many as header tokens
    expected = np.array(expected, dtype=float).reshape(nspin, nk, nb, ncomp, -1, len(header.split()))
    return "\n".join(lines) + "\n", expected


def rand_data(nspin, nk, nb, ncomp, nions, norb, seed=0):
    rng = np.random.default_rng(seed)
    vals = np.round(rng.random((nspin, nk, nb, ncomp, nions, norb)), 3)
    return vals.tolist()


def test_nonspin_layout(tmp_path):
    text, expected = make_procar(rand_data(1, 2, 3, 1, 2, 9))
    path = tmp_path / "PROCAR"
    path.write_text(text)
    spd = parse_procar(str(path))
    assert spd.shape == (2, 3, 1, 3, 11)
    # expected[spin, k, band, comp, row, col] -> spd[k, band, comp, row, col]
    np.testing.assert_array_equal(spd, expected[0])
    assert (spd[:, :, :, -1, 0] == 0).all()  # "tot" row carries ion index 0
    assert (spd[:, :, :, :2, 0] == [1, 2]).all()


def test_spin_polarized_layout(tmp_path):
    data = rand_data(2, 1, 2, 1, 2, 9)
    text, expected = make_procar(data)
    path = tmp_path / "PROCAR"
    path.write_text(text)
    spd = parse_procar(str(path))
    up, down = expected[0][:, :, 0], expected[1][:, :, 0]
    assert spd.shape == (1, 4, 2, 3, 11)
    np.testing.assert_array_equal(spd[:, :2, 0], up)
    np.testing.assert_array_equal(spd[:, 2:, 0], down)
    np.testing.assert_array_equal(spd[:, :2, 1], up)
    np.testing.assert_array_equal(spd[:, 2:, 1], -down)


def test_noncollinear_layout(tmp_path):
    text, expected = make_procar(rand_data(1, 2, 2, 4, 3, 9))
    path = tmp_path / "PROCAR"
    path.write_text(text)
    spd = parse_procar(str(path))
    assert spd.shape == (2, 2, 4, 4, 11)
    np.testing.assert_array_equal(spd, expected[0])


def test_vasp6_blank_lines_between_noncollinear_blocks(tmp_path):
    data = rand_data(1, 2, 2, 4, 3, 9)
    text, expected = make_procar(data, blank_between=True)
    assert "\n\n    1 " in text
    path = tmp_path / "PROCAR"
    path.write_text(text)
    spd = parse_procar(str(path))
    assert spd.shape == (2, 2, 4, 4, 11)
    np.testing.assert_array_equal(spd, expected[0])


def test_partial_block_is_detected(tmp_path):
    text, _ = make_procar(rand_data(1, 1, 3, 4, 2, 9))
    # drop the mx/my/mz blocks of the second band only: must not be parsed as a
    # collinear file
    lines = text.splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith("ion")]
    del lines[starts[1] + 4: starts[1] + 13]
    path = tmp_path / "PROCAR"
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(ValueError):
        parse_procar(str(path))


def test_f_orbitals(tmp_path):
    header = ("ion      s     py     pz     px    dxy    dyz    dz2    dxz  x2-y2  fy3x2   fxyz"
              "   fyz2    fz3   fxz2   fzx2    fx3    tot")
    text, expected = make_procar(rand_data(1, 1, 2, 1, 2, 16), header=header)
    path = tmp_path / "PROCAR"
    path.write_text(text)
    spd = parse_procar(str(path))
    assert spd.shape == (1, 2, 1, 3, 18)
    np.testing.assert_array_equal(spd, expected[0])


def test_lorbit10(tmp_path):
    text, expected = make_procar(rand_data(1, 1, 2, 1, 2, 3), header=HEADER_LORBIT10)
    path = tmp_path / "PROCAR"
    path.write_text(text)
    spd = parse_procar(str(path))
    assert spd.shape == (1, 2, 1, 3, 5)
    np.testing.assert_array_equal(spd, expected[0])


@pytest.mark.parametrize("tot_row", [False, True])
def test_single_ion_has_no_tot_row(tmp_path, tot_row):
    text, expected = make_procar(rand_data(1, 2, 2, 1, 1, 9), tot_row=tot_row)
    path = tmp_path / "PROCAR"
    path.write_text(text)
    spd = parse_procar(str(path))
    assert spd.shape == (2, 2, 1, 1, 11)
    np.testing.assert_array_equal(spd, expected[0])


def test_single_ion_noncollinear(tmp_path):
    text, expected = make_procar(rand_data(1, 1, 2, 4, 1, 9), tot_row=False)
    path = tmp_path / "PROCAR"
    path.write_text(text)
    spd = parse_procar(str(path))
    assert spd.shape == (1, 2, 4, 1, 11)
    np.testing.assert_array_equal(spd, expected[0])


def test_phase_factor_blocks_are_skipped(tmp_path):
    data = rand_data(1, 1, 2, 1, 2, 9)
    plain, expected = make_procar(data)
    with_phase, _ = make_procar(data, phase=True)
    assert with_phase != plain
    path = tmp_path / "PROCAR"
    path.write_text(with_phase)
    np.testing.assert_array_equal(parse_procar(str(path)), expected[0])


def test_gzip_and_directory_inputs(tmp_path):
    text, expected = make_procar(rand_data(1, 1, 2, 1, 2, 9))
    with gzip.open(tmp_path / "PROCAR.gz", "wt") as f:
        f.write(text)
    np.testing.assert_array_equal(parse_procar(str(tmp_path / "PROCAR.gz")), expected[0])
    # a missing plain file falls back to its .gz sibling, a directory to its PROCAR
    np.testing.assert_array_equal(parse_procar(str(tmp_path / "PROCAR")), expected[0])
    np.testing.assert_array_equal(parse_procar(str(tmp_path)), expected[0])


def test_missing_trailing_newline(tmp_path):
    text, expected = make_procar(rand_data(1, 1, 2, 1, 2, 9))
    path = tmp_path / "PROCAR"
    path.write_text(text.rstrip("\n"))
    np.testing.assert_array_equal(parse_procar(str(path)), expected[0])


def test_repair(tmp_path):
    src = tmp_path / "PROCAR"
    out = tmp_path / "PROCAR_repaired"
    src.write_text(
        " k-point    61 :    0.00000000-0.50000000 0.33333333     weight = 0.00003704\n"
        "band *** # energy    6.49554019 # occ.  0.00000000\n"
        "    1  0.079-0.001  0.000 ****** 0.000\n"
    )
    repair_procar(str(src), str(out))
    assert out.read_text() == (
        " k-point    61 :    0.00000000 -0.50000000 0.33333333     weight = 0.00003704\n"
        "band  1000 # energy    6.49554019 # occ.  0.00000000\n"
        "    1  0.079 -0.001  0.000  -10.0000  0.000\n"
    )
    # a well-formed file is copied unchanged
    text, _ = make_procar(rand_data(1, 1, 2, 1, 2, 9))
    src.write_text(text)
    repair_procar(str(src), str(out))
    assert out.read_text() == text


def test_repair_then_parse_roundtrip(tmp_path):
    text, expected = make_procar(rand_data(1, 2, 2, 1, 2, 9))
    src = tmp_path / "PROCAR"
    src.write_text(text.replace("0.00000000 0.00000001", "0.00000000-0.00000001"))
    repair_procar(str(src), str(tmp_path / "PROCAR_repaired"))
    np.testing.assert_array_equal(parse_procar(str(tmp_path / "PROCAR_repaired")), expected[0])


def test_inconsistent_file_raises(tmp_path):
    text, _ = make_procar(rand_data(1, 1, 2, 1, 2, 9))
    path = tmp_path / "PROCAR"
    path.write_text(text.replace("# of bands:    2", "# of bands:    3"))
    with pytest.raises(ValueError):
        parse_procar(str(path))
    with pytest.raises(FileNotFoundError):
        parse_procar(str(tmp_path / "nonexistent"))
