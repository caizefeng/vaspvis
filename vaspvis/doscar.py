"""Reader for VASP ``DOSCAR`` files.

This module replaces the ``pychemia`` dependency of earlier vaspvis releases.
:func:`parse_doscar` returns the same dictionary of arrays as
``pychemia.code.vasp.doscar.VaspDoscar.parse_doscar`` did, so results are
unchanged.
"""

import os
import re

import numpy as np

__all__ = ["parse_doscar"]

# emin (F16.8) immediately followed by a five-digit NEDOS, e.g. -47.5056123530001
_FUSED_EMIN_NEDOS = re.compile(r"^(-?\d+\.\d{8})(\d+)$")


def _read_nedos(line):
    """Return NEDOS from a DOSCAR block header line (``emax emin nedos efermi 1.0``).

    VASP writes that line with the Fortran format ``2F16.8, I5, 2F16.8``, so a
    NEDOS of 10000 or more fills its field completely and runs into ``emin``
    (``-47.5056123530001`` for emin = -47.50561235 and NEDOS = 30001).  Such a
    header is split here; pychemia's parser read the next field instead and
    looped forever on those files.
    """
    fields = line.split()
    if len(fields) >= 5:
        nedos = int(float(fields[2]))
    else:
        fused = _FUSED_EMIN_NEDOS.match(fields[1]) if len(fields) == 4 else None
        if fused is None:
            raise ValueError(f"Cannot read the DOSCAR block header: {line!r}")
        nedos = int(fused.group(2))
    if nedos <= 0:
        raise ValueError(f"Invalid NEDOS in the DOSCAR block header: {line!r}")
    return nedos


def _read_block(lines, start):
    """Read one DOS block whose header line (``emax emin nedos efermi 1.0``)
    is ``lines[start]``.  Returns the block as a 2D array and the index of
    the line following it."""
    nedos = _read_nedos(lines[start])
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
