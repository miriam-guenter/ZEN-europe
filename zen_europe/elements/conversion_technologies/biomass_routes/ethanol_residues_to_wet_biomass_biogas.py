from .biomass_route import BiomassRoute


class EthanolResiduesToWetBiomassBiogas(BiomassRoute):
    """Dummy route of ethanol_residues into wet_biomass_biogas."""

    name: str = "ethanol_residues_to_wet_biomass_biogas"
    feedstock = "ethanol_residues"
    pool = "wet_biomass_biogas"
