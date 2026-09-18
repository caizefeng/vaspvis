import numpy as np

from vaspvis.dos import _interpolate_layers


def test_layer_interpolation_reproduces_cubic_polynomials():
    # A bicubic interpolating spline reproduces any polynomial of degree <= 3
    # in each variable exactly, so the interpolated values must match it.
    layers = range(6)
    energies = np.linspace(-2.0, 3.0, 41)
    x, y = np.meshgrid(layers, energies)
    poly = lambda x, y: 0.5 * x**3 - 1.5 * x * y + 2.0 * y**2 - x**2 * y + 3.0
    densities = poly(x, y)  # shape (len(energies), len(layers))

    new_layers, interpolated = _interpolate_layers(layers, energies, densities)

    assert new_layers.shape == (50,)
    np.testing.assert_allclose(new_layers, np.arange(0, 5, 0.1))
    assert interpolated.shape == (len(energies), 50)
    xn, yn = np.meshgrid(new_layers, energies)
    np.testing.assert_allclose(interpolated, poly(xn, yn), rtol=0, atol=1e-8)


def test_layer_interpolation_keeps_grid_values():
    rng = np.random.default_rng(0)
    layers = range(2, 10)
    energies = np.linspace(-1.0, 1.0, 25)
    densities = rng.random((len(energies), len(layers)))
    new_layers, interpolated = _interpolate_layers(layers, energies, densities)
    # every original layer except the last one (np.arange excludes the stop) is on the new axis
    for i, layer in enumerate(layers[:-1]):
        j = np.argmin(np.abs(new_layers - layer))
        np.testing.assert_allclose(interpolated[:, j], densities[:, i], rtol=0, atol=1e-10)
