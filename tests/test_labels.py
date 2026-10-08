"""Typography of legend and k-path labels: elements, atom indices and high-symmetry points upright, orbitals italic."""
import pytest

from vaspvis.labels import format_legend_label, format_kpoint_label


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Pb", r"$\mathrm{Pb}$"),                       # element symbol: upright
        ("As", r"$\mathrm{As}$"),
        (3, r"$\mathrm{3}$"),                           # atom index: upright
        ("s", "$s$"),                                   # orbital letters: italic
        ("p_{x}", "$p_{x}$"),
        ("d_{x^{2}-y^{2}}", "$d_{x^{2}-y^{2}}$"),
        ("Pb(s)", r"$\mathrm{Pb}(s)$"),                 # element + orbital
        ("Pb(d_{z^{2}})", r"$\mathrm{Pb}(d_{z^{2}})$"),
        ("0(p_{x})", r"$\mathrm{0}(p_{x})$"),           # atom index + orbital
        ("$\\alpha$", "$\\alpha$"),                     # user-supplied mathtext passes through
    ],
)
def test_legend_labels(name, expected):
    assert format_legend_label(name) == expected


@pytest.mark.parametrize(
    "label, expected",
    [
        ("G", r"$\Gamma$"),
        (" G ", r"$\Gamma$"),
        ("Gamma", r"$\Gamma$"),
        ("Γ", r"$\Gamma$"),
        ("X", r"$\mathrm{X}$"),
        ("L", r"$\mathrm{L}$"),
        ("X_1", r"$\mathrm{X_1}$"),
        ("$\\Sigma_1$", "$\\Sigma_1$"),
    ],
)
def test_kpoint_labels(label, expected):
    assert format_kpoint_label(label) == expected


def test_merged_kpoint_labels_keep_a_single_mathtext_group():
    # band.py joins two coincident path ends as "<a>|<b>" and strips the inner "$|$"
    merged = "|".join([format_kpoint_label("X"), format_kpoint_label("U")]).replace("$|$", "|")
    assert merged == r"$\mathrm{X}|\mathrm{U}$"


def test_labels_are_valid_mathtext():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.mathtext import MathTextParser

    parser = MathTextParser("agg")
    for text in [
        format_legend_label("Pb(d_{x^{2}-y^{2}})"),
        format_legend_label("3(p_{x})"),
        format_legend_label("f_{y^{3}x^{2}}"),
        format_kpoint_label("G"),
        format_kpoint_label("K_1"),
        "|".join([format_kpoint_label("X"), format_kpoint_label("U")]).replace("$|$", "|"),
    ]:
        parser.parse(text)


def test_energy_axis_label_has_upright_unit_and_fermi_subscript():
    from vaspvis.labels import ENERGY_AXIS_LABEL

    assert ENERGY_AXIS_LABEL == r"$E - E_{\mathrm{F}}$ (eV)"
