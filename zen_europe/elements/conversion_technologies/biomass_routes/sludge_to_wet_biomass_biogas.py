from .biomass_route import BiomassRoute


class SludgeToWetBiomassBiogas(BiomassRoute):
    """Dummy route of sludge into wet_biomass_biogas."""

    name: str = "sludge_to_wet_biomass_biogas"
    feedstock = "sludge"
    pool = "wet_biomass_biogas"
