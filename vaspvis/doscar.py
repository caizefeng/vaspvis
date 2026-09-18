"""Reader for VASP ``DOSCAR`` files.

This module replaces the ``pychemia`` dependency of earlier vaspvis releases.
:func:`parse_doscar` returns the same dictionary of arrays as
``pychemia.code.vasp.doscar.VaspDoscar.parse_doscar`` did, so results are
unchanged.
"""

import os

import numpy as np

__all__ = ["parse_doscar"]


def _read_block(lines, start):
    """Read one DOS block whose header line (``emax emin nedos efermi 1.0``)
    is ``lines[start]``.  Returns the block as a 2D array and the index of
    the line following it."""
    header = lines[start].split()
    nedos = int(float(header[2]))
    first, last = start + 1, start + 1 + nedos
    rows = [[float(x) for x in line.split()] for line in lines[first:last]]
    return np.array(rows), last


def parse_doscar(filename):
    """Parse a DOSCAR file.

    Parameters:
        filename (str): Path of the DOSCAR file.

    Returns:
        dict: ``{"total": ndarray}`` with the total DOS block (one row per
        energy: energy, DOS, integrated DOS, with separate up and down columns
        for spin-polarised runs) and, when the file contains site-projected
        blocks (LORBIT >= 10), ``"projected"``: an array of shape
        ``(nions, nedos, ncolumns)`` holding the per-ion blocks in file order.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"DOSCAR file not found: {filename}")

    with open(filename) as f:
        lines = f.readlines()

    if len(lines) < 6:
        raise ValueError(f"DOSCAR seems truncated: {filename}")

    # Five header lines, then the total-DOS block.
    total, iline = _read_block(lines, 5)

    # Any further lines are the projected blocks, one per ion.
    projected = []
    while iline < len(lines):
        if not lines[iline].strip():
            iline += 1
            continue
        block, iline = _read_block(lines, iline)
        projected.append(block)

    if projected:
        return {"total": total, "projected": np.array(projected)}
    return {"total": total}
