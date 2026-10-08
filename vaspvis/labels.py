"""Typography of the text labels vaspvis writes on its plots.

Conventions (IUPAC/ISO 80000, ACS and APS house styles):

* symbols that are *labels* rather than physical quantities are set upright (roman): chemical element symbols
  (``Pb``), atom indices (``3``) and the high-symmetry points of the Brillouin zone (``Γ``, ``X``, ``L``, ``W``, ``K``);
* orbital letters are set in italics, as in ``s``, ``p_x``, ``d_{xy}``, ``d_{z^2}`` (ACS/APS usage, ``$p$ states``).

Everything stays inside matplotlib's mathtext so that subscripts, superscripts and Greek letters in the labels keep
working (``$\\mathrm{Pb}(d_{z^{2}})$``, ``$\\mathrm{X_{1}}$``).
"""
import re

__all__ = ["format_legend_label", "format_kpoint_label", "ENERGY_AXIS_LABEL"]

# energy axis of the standard plots: the Fermi subscript is a label and the unit is not a quantity -> both upright
ENERGY_AXIS_LABEL = "$E - E_{\\mathrm{F}}$ (eV)"

_GAMMA = {"G", "Gamma", "GAMMA", "\\Gamma", "Γ", "$\\Gamma$"}
_PREFIXED = re.compile(r"^(?P<prefix>[^()]+)\((?P<orbital>.*)\)$")      # "Pb(s)", "3(p_{x})", "Pb(d_{z^{2}})"
_ELEMENT_OR_INDEX = re.compile(r"^(?:[A-Z][a-z]?\d*|\d+)$")                 # "Pb", "Pb1", "3"


def format_legend_label(name):
    """Mathtext legend label for an element, atom index or orbital projection name.

    ``Pb`` -> ``$\\mathrm{Pb}$`` (upright), ``3`` -> ``$\\mathrm{3}$``, ``s`` / ``p_{x}`` -> ``$s$`` / ``$p_{x}$`` (italic),
    ``Pb(p_{x})`` -> ``$\\mathrm{Pb}(p_{x})$`` (upright element, italic orbital).  Anything already wrapped in ``$`` is
    returned unchanged so callers may pass their own mathtext.
    """
    name = str(name).strip()
    if name.startswith("$") and name.endswith("$"):
        return name
    m = _PREFIXED.match(name)
    if m:
        return f"$\\mathrm{{{m.group('prefix').strip()}}}({m.group('orbital').strip()})$"
    if _ELEMENT_OR_INDEX.match(name):
        return f"$\\mathrm{{{name}}}$"
    return f"${name}$"


def format_kpoint_label(label):
    """Mathtext tick label for a high-symmetry k-point: ``G`` (or ``Gamma``/``Γ``) -> ``$\\Gamma$``, everything else
    upright, keeping subscripts (``X_1`` -> ``$\\mathrm{X_1}$``).  Labels already wrapped in ``$`` are returned unchanged."""
    label = str(label).strip()
    if label in _GAMMA:
        return "$\\Gamma$"
    if label.startswith("$") and label.endswith("$"):
        return label
    return f"$\\mathrm{{{label}}}$"
