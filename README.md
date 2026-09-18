# vaspvis

A highly flexible and customizable library for visualizing electronic structure data from VASP calculations.

# Usage

This package was designed to give VASP users a flexible and easy to understand method
for generating a wide variety of band structures and density of states plots. The main
modules in this package are:

- `Band`
- `Dos`
- `standard`
- `utils`

The `Band` and `Dos` modules allow for the highest level of flexibility because the user
needs to pass in their own matplotlib axis, letting the user completely design the
external appearance of their plot. The `Band` and `Dos` modules will then parse the
VASP output data and append it to the axis.

The `standard` module uses the `Band` and `Dos` modules internally and
was designed for those people who are not familiar with matplotlib
or don't need to completely customize their own figure. There are a total of 56 different
styles of plots to choose from in this module. It gives the user the capability to project
onto any orbital, any atom, or any element in their structure, as well as individual orbitals
on any atom or element. There are also options for spin polarized band structures and density
of states as well, letting the user make intricate plots with only a few lines of code.

The `utils` module contains helper functions, for example to generate the files for band unfolding
calculations, to build and passivate slab structures, and to determine band gaps.

The package also provides the `STM` class for simulated STM images and the `Charge` class for charge
transfer analysis.

# Installation

```bash
pip install vaspvis
```

# How to Cite

To cite VaspVis please reference the following paper:

https://link.aps.org/doi/10.1103/PhysRevMaterials.5.064606

# Loading Data

```python
from vaspvis import Band, Dos

# Plain band structure
bs = Band(folder='path to vasp output folder')


# Projected band structure
bs_projected = Band(folder='path to vasp output folder', projected=True)


# Density of states (projected or non-projected)
dos = Dos(folder='path to vasp output folder')
```

**Important Note:** Band structures are parsed from the EIGENVAL, PROCAR, KPOINTS, POSCAR, INCAR, and OUTCAR files,
and densities of states from the DOSCAR, POSCAR, INCAR, and OUTCAR files (the Fermi level is read from OUTCAR). Be sure
that they are in the folder you load into vaspvis.

**Important Note:** For spin projected orbitals you must load the spin up and spin down channels separately using the `spin = 'up'` or `spin = 'down'` options when loading data. Default is `spin = 'up'`.

# Band Unfolding

Band unfolding is useful for visualizing band structures of supercells and slab structures. The method used for calculating the band unfolded structure requires an integer transformation matrix from the bulk structure. To convert the slab structure so it has an integer matrix, the `convert_slab` function can be used to generate the new slab structure and also return the transformation matrix (M). More information about the band unfolding method can be found [here](https://gpaw.readthedocs.io/tutorialsexercises/electronic/unfold/unfold.html).

```python
from vaspvis.utils import convert_slab

# This function returns and prints out the transformation matrix (M)
M = convert_slab(
    bulk_path='POSCAR_bulk', # POSCAR of the primitive bulk structure
    slab_path='POSCAR_slab', # POSCAR of the slab structure
    index=[1,1,1], # Miller index of the given slab structure
)
```

To generate the KPOINTS file for the band unfolded calculation the `generate_kpoints` function can be used

```python
from vaspvis.utils import generate_kpoints

high_symmetry_points = [
    [0.5,0.0,0.5], # X
    [0.0,0.0,0.0], # Gamma
    [0.5,0.0,0.5], # X
]

generate_kpoints(
    M=M, # M can be generated with the convert slab function
    high_symmetry_points=high_symmetry_points, # Special points
    n=50, # Number of segments between each special point
)
```

To plot the band structure the `Band` or `standard` module can be used. An example using the standard module is shown below.

```python
from vaspvis import standard as st

band_folder = 'PATH_TO_VASP_FOLDER'

# Transformation matrix generated from convert_slab
M = [
    [0,1,-1],
    [1,-1,0],
    [-8,-8,-8]
]

high_symm_points = [
    [0.5, 0.0, 0.5], # X
    [0.0, 0.0, 0.0], # Gamma
    [0.5, 0.0, 0.5]  # X
]

# All other functions in the standard library work with band unfolding too.
st.band_plain(
    folder=band_folder,
    erange=[-4,0],
    unfold=True,
    kpath=[['X', 'G'], ['G', 'X']],
    high_symm_points=high_symm_points,
    n=50,
    M=M,
)
```

# Examples

The plots below were generated with exactly the code shown, from a band structure and a density of states
calculation of InAs (PBE with spin-orbit coupling). `scale_factor` sets the size of the projection markers.
The legend is drawn beside the axes but inside the figure, so the examples with a legend use a wider `figsize`;
this keeps the axes the same size in every plot.

```python
band_folder = 'path to the band structure calculation'
dos_folder = 'path to the density of states calculation'
```

## Band Structures

### Plain Band Structure

```python
from vaspvis import standard

standard.band_plain(
    folder=band_folder
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_plain.png" width="480">

### s, p, d Projected Band Structure

```python
from vaspvis import standard

standard.band_spd(
    folder=band_folder,
    scale_factor=40,
    figsize=(4.43, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_spd.png" width="532">

### Orbital Projected Band Structure

```python
from vaspvis import standard

standard.band_orbitals(
    folder=band_folder,
    orbitals=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    scale_factor=40,
    figsize=(4.76, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_orbital.png" width="571">

### Atom Projected Band Structure

```python
from vaspvis import standard

standard.band_atoms(
    folder=band_folder,
    atoms=[0, 1],
    scale_factor=40,
    figsize=(4.42, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_atoms.png" width="530">

### Atom-Orbital Projected Band Structure

```python
from vaspvis import standard

standard.band_atom_orbitals(
    folder=band_folder,
    atom_orbital_dict={0:[1,3], 1:[1,7]},
    scale_factor=40,
    figsize=(4.73, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_atom_orbitals.png" width="568">

### Atom s, p, d Projected Band Structure

```python
from vaspvis import standard

standard.band_atom_spd(
    folder=band_folder,
    atom_spd_dict={0:'spd'},
    scale_factor=40,
    figsize=(4.62, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_atom_spd.png" width="554">

### Element Projected Band Structure

```python
from vaspvis import standard

standard.band_elements(
    folder=band_folder,
    elements=['In', 'As'],
    scale_factor=40,
    figsize=(4.52, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_elements.png" width="542">

### Element s, p, d Projected Band Structure

```python
from vaspvis import standard

standard.band_element_spd(
    folder=band_folder,
    element_spd_dict={'As':'spd'},
    scale_factor=40,
    figsize=(4.70, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_element_spd.png" width="564">

### Element Orbital Projected Band Structure

```python
from vaspvis import standard

standard.band_element_orbitals(
    folder=band_folder,
    element_orbital_dict={'As':[2], 'In':[3]},
    scale_factor=40,
    figsize=(4.76, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_element_orbital.png" width="571">

## Density of States

### Plain Density of States

```python
from vaspvis import standard

standard.dos_plain(
    folder=dos_folder,
    energyaxis='x',
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/dos_plain.png" width="480">

### s, p, d Projected Density of States

```python
from vaspvis import standard

standard.dos_spd(
    folder=dos_folder,
    energyaxis='x',
    figsize=(4.44, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/dos_spd.png" width="533">

### Orbital Projected Density of States

```python
from vaspvis import standard

standard.dos_orbitals(
    folder=dos_folder,
    orbitals=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    energyaxis='x',
    figsize=(4.77, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/dos_orbitals.png" width="572">

### Atom Projected Density of States

```python
from vaspvis import standard

standard.dos_atoms(
    folder=dos_folder,
    atoms=[0, 1],
    energyaxis='x',
    figsize=(4.43, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/dos_atoms.png" width="532">

### Atom-Orbital Projected Density of States

```python
from vaspvis import standard

standard.dos_atom_orbitals(
    folder=dos_folder,
    atom_orbital_dict={0:[1,3], 1:[1,7]},
    energyaxis='x',
    figsize=(4.74, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/dos_atom_orbitals.png" width="569">

### Atom s, p, d Projected Density of States

```python
from vaspvis import standard

standard.dos_atom_spd(
    folder=dos_folder,
    atom_spd_dict={0:'spd'},
    energyaxis='x',
    figsize=(4.63, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/dos_atom_spd.png" width="556">

### Element Projected Density of States

```python
from vaspvis import standard

standard.dos_elements(
    folder=dos_folder,
    elements=['In', 'As'],
    energyaxis='x',
    figsize=(4.53, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/dos_elements.png" width="544">

### Element s, p, d Projected Density of States

```python
from vaspvis import standard

standard.dos_element_spd(
    folder=dos_folder,
    element_spd_dict={'As':'spd'},
    energyaxis='x',
    figsize=(4.71, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/dos_element_spd.png" width="565">

### Element Orbital Projected Density of States

```python
from vaspvis import standard

standard.dos_element_orbitals(
    folder=dos_folder,
    element_orbital_dict={'As':[2], 'In':[3]},
    energyaxis='x',
    figsize=(4.77, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/dos_element_orbitals.png" width="572">

## Band Structure / Density of States

### Plain Band Structure / Density of States

```python
from vaspvis import standard

standard.band_dos_plain(
    band_folder=band_folder,
    dos_folder=dos_folder,
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_dos_plain.png" width="720">

### s, p, d Projected Band Structure / Density of States

```python
from vaspvis import standard

standard.band_dos_spd(
    band_folder=band_folder,
    dos_folder=dos_folder,
    scale_factor=40,
    figsize=(6.50, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_dos_spd.png" width="780">

### Orbital Projected Band Structure / Density of States

```python
from vaspvis import standard

standard.band_dos_orbitals(
    band_folder=band_folder,
    dos_folder=dos_folder,
    orbitals=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    scale_factor=40,
    figsize=(6.82, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_dos_orbitals.png" width="818">

### Atom-Orbital Projected Band Structure / Density of States

```python
from vaspvis import standard

standard.band_dos_atom_orbitals(
    band_folder=band_folder,
    dos_folder=dos_folder,
    atom_orbital_dict={0:[1,3], 1:[1,7]},
    scale_factor=40,
    figsize=(6.79, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_dos_atom_orbitals.png" width="815">

### Atom Projected Band Structure / Density of States

```python
from vaspvis import standard

standard.band_dos_atoms(
    band_folder=band_folder,
    dos_folder=dos_folder,
    atoms=[0, 1],
    scale_factor=40,
    figsize=(6.49, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_dos_atoms.png" width="779">

### Element Projected Band Structure / Density of States

```python
from vaspvis import standard

standard.band_dos_elements(
    band_folder=band_folder,
    dos_folder=dos_folder,
    elements=['In', 'As'],
    scale_factor=40,
    figsize=(6.58, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_dos_elements.png" width="790">

### Element s, p, d Projected Band Structure / Density of States

```python
from vaspvis import standard

standard.band_dos_element_spd(
    band_folder=band_folder,
    dos_folder=dos_folder,
    element_spd_dict={'As':'spd'},
    scale_factor=40,
    figsize=(6.77, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_dos_element_spd.png" width="812">

### Element Orbital Projected Band Structure / Density of States

```python
from vaspvis import standard

standard.band_dos_element_orbitals(
    band_folder=band_folder,
    dos_folder=dos_folder,
    element_orbital_dict={'As':[2], 'In':[3]},
    scale_factor=40,
    figsize=(6.82, 3),
)
```

<img src="https://raw.githubusercontent.com/caizefeng/vaspvis/master/img/band_dos_element_orbitals.png" width="818">
