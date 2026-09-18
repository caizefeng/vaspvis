import numpy as np

from vaspvis.dos_helpers import integrate_dos_fine


def test_integrate_constant_dos_around_fermi_level():
    energies = np.linspace(-5.0, 5.0, 201)
    tdos = np.column_stack([energies, np.full_like(energies, 2.0)])
    # a constant DOS of 2 states/eV over a window of 2 * delta = 1 eV holds 2 states
    assert np.isclose(integrate_dos_fine(tdos, E_f=0.0, delta=0.5), 2.0)
    assert np.isclose(integrate_dos_fine(tdos, E_f=0.0, delta=0.5, interpolate=False), 2.0)
    assert np.isclose(integrate_dos_fine(tdos, E_f=0.0, delta=0.5, valence_only=True), 1.0)
