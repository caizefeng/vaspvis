import vaspvis.warnings_config
import numpy as np


def integrate_dos_fine(tdos_array, E_f, delta, valence_only=False, num_points=2001, interpolate=True):
    """
    Interpolate DOS onto a finer grid and integrate it in the window.

    Parameters
    ----------
    tdos_array : np.ndarray of shape (N, 2)
        tdos_array[:, 0] -> energies (eV)
        tdos_array[:, 1] -> DOS(E)
    E_f : float
        Fermi energy (eV).
    delta : float
        Half-width of the integration window around E_f (eV).
    valence_only : bool, optional
        If True, only integrate from (E_f - delta) to the Fermi level (E_f).
        If False, integrate from (E_f - delta) to (E_f + delta).
        Default is False.
    num_points : int, optional
        Number of points in the finer energy grid for interpolation.
        Default is 2001. Won't be used if `interpolate` is False.
    interpolate : bool, optional
        If True, interpolate the DOS onto a finer grid before integration.
        If False, use the original DOS data directly.

    Returns
    -------
    float
        The integral of DOS over the specified energy window.
    """
    # Unpack energies and DOS
    energies = tdos_array[:, 0]
    dos = tdos_array[:, 1]

    # Sort data by energy (if not already sorted)
    sort_indices = np.argsort(energies)
    energies = energies[sort_indices]
    dos = dos[sort_indices]

    # Define the exact boundaries
    E_min_window = E_f - delta
    if valence_only:
        E_max_window = E_f  # For valence-only, we only integrate up to the Fermi level
    else:
        E_max_window = E_f + delta

    # Safety check: ensure the chosen window is within the overall data range
    E_min_data, E_max_data = energies[0], energies[-1]
    if E_min_window < E_min_data or E_max_window > E_max_data:
        print("WARNING: The requested integration window extends beyond the DOS data range.")
        # You can decide how to handle this, e.g., clamp to data range or raise an exception.

    # We will create a finer grid that definitely includes [E_min_window, E_max_window].
    # For best results, let's make sure it covers at least the entire data range so we can
    # safely interpolate within it. Then we'll mask to the integration window afterward.
    E_fine_min = max(E_min_data, E_min_window)
    E_fine_max = min(E_max_data, E_max_window)

    if interpolate:
        # Create a finer energy grid (linear spacing)
        E_fine = np.linspace(E_fine_min, E_fine_max, num=num_points)

        # Interpolate the DOS onto this finer grid
        dos_fine = np.interp(E_fine, energies, dos)

        # Now, mask exactly within [E_f - delta, E_f + delta]
        mask = (E_fine >= E_min_window) & (E_fine <= E_max_window)
        E_in = E_fine[mask]
        dos_in = dos_fine[mask]

        # Integrate using the trapezoidal rule
        integral_value = np.trapz(dos_in, x=E_in)
    else:
        # If not interpolating, we directly use the original data
        mask = (energies >= E_min_window) & (energies <= E_max_window)
        E_in = energies[mask]
        dos_in = dos[mask]

        # Integrate using the trapezoidal rule
        integral_value = np.trapz(dos_in, x=E_in)

    return integral_value
