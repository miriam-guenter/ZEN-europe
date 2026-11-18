from .biomass_route import BiomassRoute


class WetBiomassBiogasToBiogasFeedstock(BiomassRoute):
    """Dummy route of wet_biomass_biogas into biogas_feedstock."""

    name: str = "wet_biomass_biogas_to_biogas_feedstock"
    feedstock = "wet_biomass_biogas"
    pool = "biogas_feedstock"
