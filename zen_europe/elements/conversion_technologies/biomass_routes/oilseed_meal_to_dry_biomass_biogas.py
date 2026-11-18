from .biomass_route import BiomassRoute


class OilseedMealToDryBiomassBiogas(BiomassRoute):
    """Dummy route of oilseed_meal into dry_biomass_biogas. The protein-rich meal
    is only suited as a co-substrate: digested alone, the ammonia released from
    the proteins inhibits the process (Kolesarova et al. 2013), which the
    co-digestion mix limits via the maximum share of dry biomass."""

    name: str = "oilseed_meal_to_dry_biomass_biogas"
    feedstock = "oilseed_meal"
    pool = "dry_biomass_biogas"
