from .biomass_route import BiomassRoute


class SrcCropsToSolidBiomass(BiomassRoute):
    """Route of src_crops into solid_biomass. ENSPRESO gives the road-side cost
    of whole stems, so chipping is added."""

    name: str = "src_crops_to_solid_biomass"
    feedstock = "src_crops"
    pool = "solid_biomass"
    pretreatment_steps = [
        {
            "name": "chipping",
            "cost": 54.0,  # EUR2010/t
            "lhv": 14.15,  # GJ/t, woody perennials
            "share": 1.0,
            "year": 2010,
            "source": (
                "Ruiz et al. (2015), JRC-EU-TIMES bioenergy potentials, Table 18; "
                "LHV from Annex 5, Table 26"
            ),
        },
    ]
