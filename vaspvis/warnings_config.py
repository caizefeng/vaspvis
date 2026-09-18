"""Package-wide warning filters.

Earlier releases silenced a ``PyVistaDeprecationWarning`` that pyprocar
triggered at import time.  pyprocar (and with it pyvista) is no longer a
dependency, so there is currently nothing to filter; the module is kept so that
``import vaspvis.warnings_config`` keeps working.
"""
