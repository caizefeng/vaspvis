"""Reader for VASP ``PROCAR`` files.

This module replaces the ``pyprocar`` dependency of earlier vaspvis releases.
Only the two pieces of pyprocar that vaspvis relied on are provided: a repair
step that makes the fixed-width Fortran output whitespace-separable
(:func:`repair_procar`) and a parser that returns the projections as a single
NumPy array (:func:`parse_procar`).  The array layout is identical to
``pyprocar.ProcarParser.spd`` of pyprocar 5.6.6, so results are unchanged.
"""

import gzip
import os
import re

import numpy as np

__all__ = ["repair_procar", "parse_procar"]


def _open_text(filename):
    """Open ``filename`` for reading text, accepting gzip-compressed files.

    A directory is completed with ``PROCAR``; if ``filename`` does not exist but
    ``filename + ".gz"`` does, the compressed copy is used instead.
    """
    if os.path.isdir(filename):
        filename = os.path.join(filename, "PROCAR")
    if os.path.isfile(filename):
        if filename.endswith("gz"):
            return gzip.open(filename, mode="rt")
        return open(filename, "r")
    if os.path.isfile(filename + ".gz"):
        return gzip.open(filename + ".gz", mode="rt")
    raise FileNotFoundError(f"PROCAR file not found: {filename}")


_BAND_INDEX_OVERFLOW = re.compile(r"(band\s)(\*\*\*)")
_FUSED_KPOINT_COORDS = re.compile(r"(\.\d{8})(\d{2}\.)")
_FUSED_NEGATIVE = re.compile(r"(\d)-(\d)")
_ASTERISKS = re.compile(r"\*+")


def repair_procar(infilename, outfilename):
    """Write a copy of a PROCAR file in which every field is whitespace-separated.

    VASP writes PROCAR with fixed-width Fortran formats, so neighbouring numbers
    can run into each other (``0.00000000-0.50000000`` in a k-point line) and
    values too wide for their field are printed as asterisks.  The substitutions
    below are exactly the ones pyprocar's ``UtilsProcar.ProcarRepair`` applied,
    so a newly repaired file is identical to one produced by earlier releases:

    * ``band ***`` (band index >= 1000) becomes ``band  1000``
    * two k-point coordinates fused together are separated by a space
    * a negative number fused to the preceding field is separated
    * any remaining run of asterisks becomes `` -10.0000 ``

    Parameters:
        infilename (str): PROCAR file (or a ``.gz`` copy, or a directory
            containing one).
        outfilename (str): Path of the repaired copy to write.
    """
    with _open_text(infilename) as f:
        text = f.read()

    text = _BAND_INDEX_OVERFLOW.sub(r"\1 1000", text)
    text = _FUSED_KPOINT_COORDS.sub(r"\1 \2", text)
    text = _FUSED_NEGATIVE.sub(r"\1 -\2", text)
    text = _ASTERISKS.sub(" -10.0000 ", text)

    with open(outfilename, "w") as f:
        f.write(text)


# One k-point header per k-point (twice that for a collinear spin-polarised
# run, which writes the whole file once per spin channel).
_KPOINT_HEADER = re.compile(r"^\s*k-point\s+\S+\s*:(.*)$", re.MULTILINE)
# One band header per (k-point, band[, spin channel]).
_BAND_HEADER = re.compile(r"^\s*band\s+\S+\s*#\s*energy", re.MULTILINE)
# A projection header (``ion  s  py ... tot``) followed by its data rows: one
# row per ion plus a ``tot`` row, repeated four times (total, mx, my, mz) for
# non-collinear runs.  VASP 6 separates those four blocks with a blank line, so
# whitespace-only lines are allowed between rows.  The phase-factor blocks
# written for LORBIT = 12 have a header without ``tot`` and are therefore
# skipped, as pyprocar did.
_PROJECTION_BLOCK = re.compile(
    r"^ion[ \t]+(?P<orbitals>\S.*?\btot)[ \t]*\n"
    r"(?P<rows>(?:(?:[ \t]*\n)*[ \t]*(?:\d+|tot)[ \t]+[^\n]*(?:\n|\Z))+)",
    re.MULTILINE,
)


def parse_procar(filename):
    """Parse a (repaired) PROCAR file into an array of projections.

    Parameters:
        filename (str): PROCAR file, normally the copy written by
            :func:`repair_procar`.  Gzip-compressed files are accepted.

    Returns:
        numpy.ndarray: Array ``spd`` of shape
        ``(nkpoints, nbands, nspin, nrows, norbitals + 2)`` laid out exactly
        like ``pyprocar.ProcarParser.spd``:

        * ``nspin`` is 1 for a non-spin-polarised run; 4 for a non-collinear
          run (total, mx, my, mz); 2 for a collinear spin-polarised run, in
          which case the up and down channels are stacked along the band axis
          (``nbands`` is then twice the number of bands), spin index 0 holds
          the projections as written and spin index 1 the same data with the
          down channel negated.
        * ``nrows`` is the number of ions plus one for the trailing ``tot``
          row (sum over ions); single-ion runs have no ``tot`` row, so
          ``nrows`` is 1 for them.
        * The last axis holds the ion index (0 for the ``tot`` row), the
          projection onto each orbital, and the total over orbitals.
    """
    with _open_text(filename) as f:
        f.readline()  # "PROCAR lm decomposed" / "PROCAR new format"
        meta = f.readline()  # "# of k-points:  816   # of bands:  52   # of ions:   8"
        text = f.read()

    counts = [int(x) for x in re.findall(r":\s*(\d+)", meta)]
    if len(counts) != 3:
        raise ValueError(f"Cannot read the PROCAR header line: {meta!r}")
    nkpoints, nbands, nions = counts

    kpoint_lines = _KPOINT_HEADER.findall(text)
    if len(kpoint_lines) == nkpoints:
        nspin = 1
    elif len(kpoint_lines) == 2 * nkpoints:
        up, down = kpoint_lines[:nkpoints], kpoint_lines[nkpoints:]
        if [line.split() for line in up] != [line.split() for line in down]:
            raise ValueError(
                "The two spin channels of the PROCAR file list different k-points"
            )
        nspin = 2
    else:
        raise ValueError(
            f"Found {len(kpoint_lines)} k-point blocks in the PROCAR file, "
            f"expected {nkpoints} (or {2 * nkpoints} for ISPIN = 2)"
        )

    nband_headers = len(_BAND_HEADER.findall(text))
    if nband_headers != nkpoints * nbands * nspin:
        raise ValueError(
            f"Found {nband_headers} band blocks in the PROCAR file, "
            f"expected {nkpoints * nbands * nspin}"
        )

    # Single-ion runs carry no "tot" row (and any that is present is ignored,
    # matching pyprocar); every other run has one after the ion rows.
    rows_per_block = nions + 1 if nions > 1 else 1
    expected_headers = nkpoints * nbands * nspin
    ncols = None
    data = None
    rows_per_header = None
    nheaders = 0
    for match in _PROJECTION_BLOCK.finditer(text):
        if ncols is None:
            # ion index + one column per orbital + "tot"
            ncols = len(match.group("orbitals").split()) + 1
        rows = []
        for row in match.group("rows").splitlines():
            fields = row.split()
            if not fields:
                continue
            if len(fields) != ncols:
                raise ValueError(
                    f"Expected {ncols} fields per projection row, found "
                    f"{len(fields)}: {row!r}"
                )
            if fields[0] == "tot":
                if nions == 1:
                    continue
                fields[0] = "0"
            rows.append(fields)
        if data is None:
            # Every block is converted as soon as it is read and stored in a
            # preallocated array, so that the peak memory stays close to the
            # size of the file plus the size of the result.
            rows_per_header = len(rows)
            data = np.empty((expected_headers, rows_per_header, ncols))
        elif len(rows) != rows_per_header:
            raise ValueError(
                f"Projection block {nheaders + 1} of the PROCAR file has "
                f"{len(rows)} rows, the first one has {rows_per_header}"
            )
        if nheaders >= expected_headers:
            raise ValueError(
                f"Found more than {expected_headers} projection blocks in the "
                "PROCAR file"
            )
        data[nheaders] = np.array(rows, dtype=float)
        nheaders += 1
    del text

    if data is None:
        raise ValueError("No orbital projections found in the PROCAR file")
    if nheaders != expected_headers:
        raise ValueError(
            f"Found {nheaders} projection blocks in the PROCAR file, expected "
            f"{expected_headers}"
        )
    if rows_per_header == rows_per_block:
        ncomponents = 1
    elif rows_per_header == 4 * rows_per_block and nspin == 1:
        ncomponents = 4
        nspin = 4
    else:
        raise ValueError(
            f"Each projection block of the PROCAR file has {rows_per_header} "
            f"rows, expected {rows_per_block} (or 4 times that for a "
            "non-collinear run)"
        )
    nblocks = nheaders * ncomponents

    data = data.reshape(nblocks, rows_per_block, ncols)

    if nspin == 2:
        half = nblocks // 2
        up = data[:half].reshape(nkpoints, nbands, 1, rows_per_block, ncols)
        down = data[half:].reshape(nkpoints, nbands, 1, rows_per_block, ncols)
        density = np.concatenate((up, down), axis=1)
        magnetization = np.concatenate((up, -down), axis=1)
        return np.concatenate((density, magnetization), axis=2)

    return data.reshape(nkpoints, nbands, nspin, rows_per_block, ncols)
