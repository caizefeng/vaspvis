import glob
import os
import re
import warnings

import numpy as np
from pymatgen.io.vasp import Outcar, Incar


def get_magmoment(calc_folder, is_true_integral=True):
    """
    Extracts the total magnetic moment from a VASP calculation output.

    Parameters:
    - calc_folder (str): Path to the folder containing VASP output files.
    - is_true_integral (bool): If True (default), read total magnetic moment
      from OSZICAR. If False, read from OUTCAR atom-resolved magnetization.

    Returns:
    - total_mag_val (float): The total magnetic moment value.
    """

    # ==========================
    # Case 1: Read from OSZICAR
    # ==========================
    if is_true_integral:
        oszicar_path = os.path.join(calc_folder, "OSZICAR")

        if not os.path.exists(oszicar_path):
            raise FileNotFoundError("OSZICAR not found in calculation folder.")

        total_mag_val = None
        with open(oszicar_path, "r") as f:
            for line in f:
                if "mag=" in line:
                    # Example:
                    # 1 F= ... mag=     0.0000    -0.0000     1.9965
                    mag_part = line.split("mag=")[1].split()
                    total_mag_val = float(mag_part[-1])

        if total_mag_val is None:
            raise ValueError("No magnetic moment found in OSZICAR.")

        return total_mag_val

    # ==========================
    # Case 2: Read from OUTCAR
    # ==========================
    outcar_path = os.path.join(calc_folder, "OUTCAR")

    # Use Outcar class to get number of atoms
    outcar = Outcar(outcar_path)
    num_atoms = len(outcar.magnetization)  # gets list of dicts per atom

    outcar_incar_format = Incar.from_file(outcar_path)
    lnoncollinear = outcar_incar_format.get("LNONCOLLINEAR", False)

    # Decide which magnetization axis to look for
    search_text = "magnetization (z)" if lnoncollinear else "magnetization (x)"

    lines = []
    capture = False
    counter = 0
    num_lines_to_read = num_atoms + 6  # header + atom lines + total line

    with open(outcar_path, 'r') as file:
        for line in file:
            if search_text in line:
                capture = True
                counter = 0
                lines = []

            if capture:
                lines.append(line)
                counter += 1
                if counter >= num_lines_to_read:
                    capture = False

    if len(lines) < num_atoms + 6:
        raise ValueError("Incomplete magnetization section found in OUTCAR.")

    # Check for presence of 'f' orbital
    spd_line = lines[2].split()
    has_f_orbital = 'f' in spd_line

    # Extract total magnetization from the last line
    mag_line = lines[5 + num_atoms].split()
    total_mag_val = float(mag_line[5] if has_f_orbital else mag_line[4])

    return total_mag_val


# function to read labels out of .gnu file from wannier-90 output, since data isnt written out in a file
def extract_letters_and_numbers(input_string):
    """
    Extracts letters and numbers from a gnuplot xtics string.

    Parameters:
        input_string (str): xtics string from .gnu file.

    Returns:
        tuple: (list of labels, list of corresponding float positions)
    """
    letters = re.findall(r'" (\w) "', input_string)
    numbers = re.findall(r'\b\d+\.\d+\b|\b\d+\b', input_string)
    numbers = [float(num) for num in numbers]

    return letters, numbers


def compare_signs(input_array, compare):
    """
    Sign function comparing elements to a reference value.

    Parameters:
        input_array (list or array): list of numbers to compare.
        compare (float): value to compare against.

    Returns:
        list: 1 if element > compare, -1 if < compare, 0 if equal.
    """
    transformed_array = []
    for number in input_array:
        transformed_array.append(bool(number > compare) - bool(number < compare))
    return transformed_array


def clean_data_GW(data_path, gw_band_folder="gw_band", wannier_suffix="_band", full_bz_folder="dos"):
    """
    Processes GW band structure data with optional spin channel.

    Parameters:
    - data_path: base path to the GW calculation directory
    - spin_channel: suffix of the band file (default: "_band")
    - gw_band_folder: folder containing GW band data
    - gw_folder: folder containing OUTCAR with Fermi energy

    Returns:
    - band_data: numpy array of band structure data
    - labels: high-symmetry point labels
    - labelx: positions of high-symmetry points on the x-axis
    - efermi: Fermi energy from OUTCAR
    """
    band_file_path = f"{data_path}/{gw_band_folder}/wannier90{wannier_suffix}.dat"
    gnu_file_path = f"{data_path}/{gw_band_folder}/wannier90{wannier_suffix}.gnu"
    outcar_band_path = f"{data_path}/{gw_band_folder}/OUTCAR"
    outcar_full_bz_path = f"{data_path}/{full_bz_folder}/OUTCAR"

    # Read .dat file
    try:
        with open(band_file_path, 'r') as f:
            raw_data = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find band data file: {band_file_path}")

    band_data = []
    for line in raw_data:
        parts = list(filter(None, line.strip().split()))
        if parts:
            band_data.append([float(x) for x in parts])

    # Read .gnu file and extract label info
    try:
        with open(gnu_file_path, 'r') as f:
            labelinfo_up = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find .gnu file: {gnu_file_path}")

    for line in labelinfo_up:
        if line.startswith("set xtics"):
            labels_labelx = line[len("set xtics"):].strip()
            break
    else:
        raise ValueError("Could not find 'set xtics' line in .gnu file.")

    labels, labelx = extract_letters_and_numbers(labels_labelx)
    labels = list(map(lambda x: x.replace('G', r"$\mathrm{\mathsf{\Gamma}}$"), labels))  # replacing G with \Gamma

    # Read NUM_WANN from OUTCAR
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            incar = Incar.from_file(outcar_band_path)
        NUM_WANN = incar["NUM_WANN"]
    except Exception as e:
        raise RuntimeError("Could not read NUM_WANN from OUTCAR") from e

    # Reshape band data
    print("Found NUM_WANN =", NUM_WANN)
    band_data = np.array(band_data).reshape((NUM_WANN, -1, 3))

    # Read Fermi energy
    efermi = Outcar(outcar_full_bz_path).efermi

    return band_data, labels, labelx, efermi


def _read_w90_3col_bands(path):
    """Read 3-column wannier90*.dat with blank lines separating bands -> list[(Nk,3)]."""
    bands, cur = [], []
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if not s:
                if cur:
                    bands.append(np.array(cur, float))
                    cur = []
                continue
            a, b, c = s.split()[:3]
            cur.append([float(a), float(b), float(c)])
    if cur:
        bands.append(np.array(cur, float))
    return bands


def _contiguous_runs(mask):
    idx = np.where(mask)[0]
    if idx.size == 0:
        return []
    breaks = np.where(np.diff(idx) > 1)[0]
    runs = np.split(idx, breaks + 1)
    return [(r[0], r[-1]) for r in runs]


def _discover_w90_orbital_folders(band_folder_path):
    """
    Find w90_o* folders and sort by the integer suffix.
    Returns list of folder paths in order.
    """
    cands = glob.glob(os.path.join(band_folder_path, "w90_o*"))
    parsed = []
    for p in cands:
        name = os.path.basename(p)
        m = re.match(r"w90_o(\d+)$", name)
        if m:
            parsed.append((int(m.group(1)), p))
    parsed.sort(key=lambda t: t[0])
    return [p for _, p in parsed]


def plot_w90_orbital_projected_spin_split_N(
        ax_up,
        ax_dn,
        data_path,
        band_folder,
        dos_folder,
        colors,  # list of colors, length N
        wannier_suffix="-bands",
        erange=(-4, 4),
        base_color="0.80",
        base_lw=0.35,
        scale_factor=40.0,
        display_order="all",  # mimic vaspvis ordering (largest markers on top)
        orbital_folders=None,  # optional: list of explicit folders (paths) to use
):
    """
    Up/down split from p90_SP/wannier90{wannier_suffix}.dat (sign of 3rd col).
    Orbital weights from each w90_o*/wannier90_band.dat (3rd col).
    Number of orbitals N = len(colors) and must match discovered folder count unless orbital_folders is provided.
    """

    band_folder_path = f"{data_path}/{band_folder}"

    # labels/fermi from clean_data_GW (preferred)
    _, labels, labelx, efermi = clean_data_GW(
        data_path,
        gw_band_folder=f"{band_folder}/p90_SP",
        wannier_suffix=wannier_suffix,
        full_bz_folder=dos_folder,
    )

    # spin-pol file
    sp_path = os.path.join(band_folder_path, "p90_SP", f"wannier90{wannier_suffix}.dat")
    sp_bands = _read_w90_3col_bands(sp_path)

    # discover orbital folders if not specified
    if orbital_folders is None:
        orbital_folders = _discover_w90_orbital_folders(band_folder_path)

    N = len(colors)
    if len(orbital_folders) < N:
        raise ValueError(f"Found only {len(orbital_folders)} w90_o* folders, but got {N} colors (need N folders).")
    if len(orbital_folders) > N:
        # only use first N by default (consistent with colors)
        orbital_folders = orbital_folders[:N]

    # read all orbital weight bands
    w_bands_all = []
    for of in orbital_folders:
        w_path = os.path.join(of, "wannier90_band.dat")
        w_bands_all.append(_read_w90_3col_bands(w_path))

    nb = len(sp_bands)
    for i in range(N):
        if len(w_bands_all[i]) != nb:
            raise ValueError(f"Band count mismatch: SP={nb}, orbital #{i + 1} has {len(w_bands_all[i])}")

    # plot
    for b in range(nb):
        sp = sp_bands[b]
        x = sp[:, 0]
        E = sp[:, 1] - efermi
        sgn = sp[:, 2]

        up_mask = sgn > 0
        dn_mask = sgn < 0

        # backbone lines
        for ax, mask in ((ax_up, up_mask), (ax_dn, dn_mask)):
            for i0, i1 in _contiguous_runs(mask):
                ax.plot(x[i0:i1 + 1], E[i0:i1 + 1], color=base_color, lw=base_lw, zorder=0)

        # overlay N orbitals as scatter-size
        for i in range(N):
            col = colors[i]
            w = w_bands_all[i][b][:, 2]

            # UP
            for i0, i1 in _contiguous_runs(up_mask):
                xv, Ev, wv = x[i0:i1 + 1], E[i0:i1 + 1], w[i0:i1 + 1]
                if display_order is None:
                    idx = np.arange(wv.size)
                else:
                    idx = np.argsort(wv)
                    if display_order == "all":
                        idx = idx[::-1]
                ax_up.scatter(
                    xv[idx], Ev[idx],
                    c=col,
                    ec=[(1, 1, 1, 0)],  # transparent edges like vaspvis
                    s=scale_factor * wv[idx],
                    zorder=100,
                )

            # DOWN
            for i0, i1 in _contiguous_runs(dn_mask):
                xv, Ev, wv = x[i0:i1 + 1], E[i0:i1 + 1], w[i0:i1 + 1]
                if display_order is None:
                    idx = np.arange(wv.size)
                else:
                    idx = np.argsort(wv)
                    if display_order == "all":
                        idx = idx[::-1]
                ax_dn.scatter(
                    xv[idx], Ev[idx],
                    c=col,
                    ec=[(1, 1, 1, 0)],
                    s=scale_factor * wv[idx],
                    zorder=100,
                )

    # ticks/labels + symmetry lines
    for ax in (ax_up, ax_dn):
        ax.vlines(labelx, erange[0], erange[1], color="black", alpha=0.7, linewidth=0.5)
        ax.set_xticks(labelx)
        ax.set_xticklabels(labels, fontdict={"fontstyle": "italic"})
        ax.set_xlim(0, max(labelx))
