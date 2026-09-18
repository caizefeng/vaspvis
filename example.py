from vaspvis import standard


band_folder = '../vaspvis_data/band_InAs'
dos_folder = '../vaspvis_data/dos_InAs'


# ==========================================================
# Plain Band Structure
# ==========================================================

standard.band_plain(
    folder=band_folder
)


# ==========================================================
# s, p, d Projected Band Structure
# ==========================================================

standard.band_spd(
    folder=band_folder,
    scale_factor=40,
    figsize=(4.43, 3),
)


# ==========================================================
# Orbital Projected Band Structure
# ==========================================================

standard.band_orbitals(
    folder=band_folder,
    orbitals=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    scale_factor=40,
    figsize=(4.76, 3),
)


# ==========================================================
# Atom Projected Band Structure
# ==========================================================

standard.band_atoms(
    folder=band_folder,
    atoms=[0, 1],
    scale_factor=40,
    figsize=(4.42, 3),
)


# ==========================================================
# Atom-Orbital Projected Band Structure
# ==========================================================

standard.band_atom_orbitals(
    folder=band_folder,
    atom_orbital_dict={0:[1,3], 1:[1,7]},
    scale_factor=40,
    figsize=(4.73, 3),
)


# ==========================================================
# Atom s, p, d Projected Band Structure
# ==========================================================

standard.band_atom_spd(
    folder=band_folder,
    atom_spd_dict={0:'spd'},
    scale_factor=40,
    figsize=(4.62, 3),
)


# ==========================================================
# Element Projected Band Structure
# ==========================================================

standard.band_elements(
    folder=band_folder,
    elements=['In', 'As'],
    scale_factor=40,
    figsize=(4.52, 3),
)


# ==========================================================
# Element s, p, d Projected Band Structure
# ==========================================================

standard.band_element_spd(
    folder=band_folder,
    element_spd_dict={'As':'spd'},
    scale_factor=40,
    figsize=(4.70, 3),
)


# ==========================================================
# Element Orbital Projected Band Structure
# ==========================================================

standard.band_element_orbitals(
    folder=band_folder,
    element_orbital_dict={'As':[2], 'In':[3]},
    scale_factor=40,
    figsize=(4.76, 3),
)


# ==========================================================
# Plain Density of States
# ==========================================================

standard.dos_plain(
    folder=dos_folder,
    energyaxis='x',
)


# ==========================================================
# s, p, d Projected Density of States
# ==========================================================

standard.dos_spd(
    folder=dos_folder,
    energyaxis='x',
    figsize=(4.44, 3),
)


# ==========================================================
# Orbital Projected Density of States
# ==========================================================

standard.dos_orbitals(
    folder=dos_folder,
    orbitals=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    energyaxis='x',
    figsize=(4.77, 3),
)


# ==========================================================
# Atom Projected Density of States
# ==========================================================

standard.dos_atoms(
    folder=dos_folder,
    atoms=[0, 1],
    energyaxis='x',
    figsize=(4.43, 3),
)


# ==========================================================
# Atom-Orbital Projected Density of States
# ==========================================================

standard.dos_atom_orbitals(
    folder=dos_folder,
    atom_orbital_dict={0:[1,3], 1:[1,7]},
    energyaxis='x',
    figsize=(4.74, 3),
)


# ==========================================================
# Atom s, p, d Projected Density of States
# ==========================================================

standard.dos_atom_spd(
    folder=dos_folder,
    atom_spd_dict={0:'spd'},
    energyaxis='x',
    figsize=(4.63, 3),
)


# ==========================================================
# Element Projected Density of States
# ==========================================================

standard.dos_elements(
    folder=dos_folder,
    elements=['In', 'As'],
    energyaxis='x',
    figsize=(4.53, 3),
)


# ==========================================================
# Element s, p, d Projected Density of States
# ==========================================================

standard.dos_element_spd(
    folder=dos_folder,
    element_spd_dict={'As':'spd'},
    energyaxis='x',
    figsize=(4.71, 3),
)


# ==========================================================
# Element Orbital Projected Density of States
# ==========================================================

standard.dos_element_orbitals(
    folder=dos_folder,
    element_orbital_dict={'As':[2], 'In':[3]},
    energyaxis='x',
    figsize=(4.77, 3),
)


# ==========================================================
# Plain Band Structure / Density of States
# ==========================================================

standard.band_dos_plain(
    band_folder=band_folder,
    dos_folder=dos_folder,
)


# ==========================================================
# s, p, d Projected Band Structure / Density of States
# ==========================================================

standard.band_dos_spd(
    band_folder=band_folder,
    dos_folder=dos_folder,
    scale_factor=40,
    figsize=(6.50, 3),
)


# ==========================================================
# Orbital Projected Band Structure / Density of States
# ==========================================================

standard.band_dos_orbitals(
    band_folder=band_folder,
    dos_folder=dos_folder,
    orbitals=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    scale_factor=40,
    figsize=(6.82, 3),
)


# ==========================================================
# Atom-Orbital Projected Band Structure / Density of States
# ==========================================================

standard.band_dos_atom_orbitals(
    band_folder=band_folder,
    dos_folder=dos_folder,
    atom_orbital_dict={0:[1,3], 1:[1,7]},
    scale_factor=40,
    figsize=(6.79, 3),
)


# ==========================================================
# Atom Projected Band Structure / Density of States
# ==========================================================

standard.band_dos_atoms(
    band_folder=band_folder,
    dos_folder=dos_folder,
    atoms=[0, 1],
    scale_factor=40,
    figsize=(6.49, 3),
)


# ==========================================================
# Element Projected Band Structure / Density of States
# ==========================================================

standard.band_dos_elements(
    band_folder=band_folder,
    dos_folder=dos_folder,
    elements=['In', 'As'],
    scale_factor=40,
    figsize=(6.58, 3),
)


# ==========================================================
# Element s, p, d Projected Band Structure / Density of States
# ==========================================================

standard.band_dos_element_spd(
    band_folder=band_folder,
    dos_folder=dos_folder,
    element_spd_dict={'As':'spd'},
    scale_factor=40,
    figsize=(6.77, 3),
)


# ==========================================================
# Element Orbital Projected Band Structure / Density of States
# ==========================================================

standard.band_dos_element_orbitals(
    band_folder=band_folder,
    dos_folder=dos_folder,
    element_orbital_dict={'As':[2], 'In':[3]},
    scale_factor=40,
    figsize=(6.82, 3),
)
