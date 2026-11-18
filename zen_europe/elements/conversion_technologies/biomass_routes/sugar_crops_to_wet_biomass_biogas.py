from .biomass_route import BiomassRoute


class SugarCropsToWetBiomassBiogas(BiomassRoute):
    """Dummy route of sugar_crops into wet_biomass_biogas."""

    name: str = "sugar_crops_to_wet_biomass_biogas"
    feedstock = "sugar_crops"
    pool = "wet_biomass_biogas"
