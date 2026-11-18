from .biomass_route import BiomassRoute


class SrcCropsToBiomassSlowPyrolysis(BiomassRoute):
    """Dummy route of src_crops into biomass_slow_pyrolysis."""

    name: str = "src_crops_to_biomass_slow_pyrolysis"
    feedstock = "src_crops"
    pool = "biomass_slow_pyrolysis"
