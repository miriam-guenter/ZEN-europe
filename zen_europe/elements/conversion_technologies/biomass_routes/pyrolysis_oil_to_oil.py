from .biomass_route import BiomassRoute


class PyrolysisOilToOil(BiomassRoute):
    """Dummy route of pyrolysis_oil into oil."""

    # TODO: interim 1:1 route; replace by an upgrading (hydrotreating) technology
    # with hydrogen demand and costs (research dataset still needed)
    name: str = "pyrolysis_oil_to_oil"
    feedstock = "pyrolysis_oil"
    pool = "oil"
