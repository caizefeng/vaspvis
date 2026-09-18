import sys


def test_import_without_optional_parsers():
    import vaspvis
    import vaspvis.standard
    import vaspvis.utils
    import vaspvis.workflow

    assert vaspvis.Band and vaspvis.Dos and vaspvis.STM and vaspvis.Charge
    assert "pyprocar" not in sys.modules
    assert "pychemia" not in sys.modules
    assert "pyvista" not in sys.modules
