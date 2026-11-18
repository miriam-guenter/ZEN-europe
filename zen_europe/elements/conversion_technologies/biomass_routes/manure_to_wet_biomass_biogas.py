from .biomass_route import BiomassRoute


class ManureToWetBiomassBiogas(BiomassRoute):
    """Dummy route of manure into wet_biomass_biogas."""

    name: str = "manure_to_wet_biomass_biogas"
    feedstock = "manure"
    pool = "wet_biomass_biogas"
