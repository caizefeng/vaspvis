import warnings

from pyvista import PyVistaDeprecationWarning

warnings.filterwarnings(
    "ignore",
    category=PyVistaDeprecationWarning,
    module=r"pyvista"  # Match the module where the warning ORIGINATED
)
