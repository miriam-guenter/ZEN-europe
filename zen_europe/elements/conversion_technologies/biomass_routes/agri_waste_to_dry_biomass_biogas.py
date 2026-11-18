from .biomass_route import BiomassRoute


class AgriWasteToDryBiomassBiogas(BiomassRoute):
    """Dummy route of agri_waste into dry_biomass_biogas."""

    name: str = "agri_waste_to_dry_biomass_biogas"
    feedstock = "agri_waste"
    pool = "dry_biomass_biogas"
