from zen_europe.elements.carriers.oilseed_meal import OilseedMeal

from .biomass_route import BiomassRoute

# Mass balance of conventional crushing (pressing + hexane extraction) of
# rapeseed, per t of seed (Carre et al. 2018, Table 5)
_OIL_YIELD = 0.446  # t crude oil / t seed
_MEAL_YIELD = 0.546  # t meal / t seed
# Heating values
_LHV_SEED = 18.62  # GJ/t, rape seed, used by ENSPRESO (Ruiz et al. 2015, Table 26)
_LHV_OIL = 36.0  # GJ/t, vegetable oil (ADEME 2010, cited in OCL 2013, Table 1)
_OIL_PER_SEED = _OIL_YIELD * _LHV_OIL  # GJ oil / t seed
_MEAL_PER_SEED = _MEAL_YIELD * OilseedMeal.lhv()  # GJ meal / t seed


class OilCropsToOilyBiomass(BiomassRoute):
    """Route of oil_crops (seed) into oily_biomass (crude vegetable oil) by
    crushing: pressing and hexane extraction of the oil, with oilseed meal as
    co-product. ENSPRESO gives the market price of the seed, while FAME and HVO
    (DEA) take vegetable oil as input."""

    name: str = "oil_crops_to_oily_biomass"
    feedstock = "oil_crops"
    pool = "oily_biomass"
    feedstock_per_pool = _LHV_SEED / _OIL_PER_SEED
    byproducts = {"oilseed_meal": _MEAL_PER_SEED / _OIL_PER_SEED}
    conversion_description = (
        f"Crushing of oilseed into crude vegetable oil and meal. Per t of rape "
        f"seed: {_OIL_YIELD} t oil and {_MEAL_YIELD} t meal (Carre et al. 2018, "
        f"Table 5). The seed is counted with the LHV used by ENSPRESO "
        f"({_LHV_SEED} GJ/t, Ruiz et al. 2015, Table 26), the oil with "
        f"{_LHV_OIL} GJ/t and the meal with {OilseedMeal.lhv():.2f} GJ/t (ADEME "
        f"2010). Rapeseed values are used for all oil crops."
    )
    pretreatment_steps = [
        {
            "name": "crushing (pressing + hexane extraction)",
            "cost": 30.0,  # EUR2017/t seed
            "lhv": _LHV_SEED,
            "share": 1.0,
            "year": 2017,
            "source": (
                "Carre et al. (2018), processing cost of conventional hexane "
                "crushing, in line with Cheng and Rosentrater (2017)"
            ),
        },
    ]
