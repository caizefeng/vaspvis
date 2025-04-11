import os
import re
import warnings

import vaspvis.warnings_config
import numpy as np
from pymatgen.io.vasp.inputs import Incar
from pymatgen.io.vasp.outputs import Outcar


def get_magmoment(calc_folder):
    """
    Extracts the total magnetic moment from a VASP calculation output.

    Parameters:
    - calc_folder (str): Path to the folder containing VASP output files.

    Returns:
    - total_mag_val (float): The total magnetic moment value.
    """
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
            data_up = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find band data file: {band_file_path}")

    band_data = []
    for line in data_up:
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

    # Read NUM_WANN from INCAR
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            incar = Incar.from_file(outcar_band_path)
        NUM_WANN = incar.get("NUM_WANN", 56)  # Default to 56 if not found
        print("Found NUM_WANN =", NUM_WANN)
    except Exception as e:
        NUM_WANN = 56
        print("Warning: Could not read OUTCAR. Using default NUM_WANN =", NUM_WANN)

    # Reshape band data
    band_data = np.array(band_data).reshape((NUM_WANN, -1, 3))

    # Read Fermi energy
    efermi = Outcar(outcar_full_bz_path).efermi

    return band_data, labels, labelx, efermi
