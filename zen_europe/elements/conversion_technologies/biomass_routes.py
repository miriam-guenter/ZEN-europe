from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import AssumptionInformation, Attribute, ConversionTechnology

# pool carrier -> feedstocks that can be routed into it (see SC_charts.drawio)
BIOMASS_ROUTES: dict[str, list[str]] = {
    "comb_biomass": [
        "stemwood", "forestry_residues", "src_crops", "perennial_grasses",
        "agri_residues_woody", "agri_residues_herb", "wood_waste",
    ],
    "dry_biomass_biogas": ["starch_crops", "perennial_grasses", "agri_residues_herb"],
    "wet_biomass_biogas": ["manure", "sugar_crops", "biowaste", "sludge"],
    "cellulosic_biomass": ["agri_residues_herb", "perennial_grasses"],
    "oily_biomass": ["oil_crops"],
    "biomass_slow_pyrolysis": [
        "stemwood", "forestry_residues", "src_crops", "perennial_grasses",
        "agri_residues_woody", "agri_residues_herb", "wood_waste",
        "biowaste", "sludge",
    ],
    "biomass_fast_pyrolysis": ["stemwood","forestry_residues", "src_crops"],
}


class BiomassRoute(ConversionTechnology):
    """Dummy technology that routes a biomass feedstock 1:1 into a dummy carrier.

    It has no costs and no capacity limits. It only makes the
    feedstock -> technology allocation visible in the results."""

    name: str = "biomass_route"
    feedstock: ClassVar[str] = ""
    pool: ClassVar[str] = ""

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_reference_carrier(self) -> Attribute:
        return Attribute(name="reference_carrier", default_value=[self.pool], element=self)

    def _set_input_carrier(self) -> Attribute:
        return Attribute(name="input_carrier", default_value=[self.feedstock], element=self)

    def _set_output_carrier(self) -> Attribute:
        return Attribute(name="output_carrier", default_value=[self.pool], element=self)

    def _set_conversion_factor(self) -> Attribute:
        attr = self.conversion_factor
        attr.set_data(
            default_value=[{self.feedstock: {"default_value": 1, "unit": "GWh/GWh"}}],
            source=AssumptionInformation(
                description=f"Lossless 1:1 routing of {self.feedstock} into {self.pool}."
            ),
        )
        return attr

    def _set_lifetime(self) -> Attribute:
        attr = self.lifetime
        attr.set_data(
            default_value=50,
            source=AssumptionInformation(
                description="Dummy technology; lifetime has no economic effect."
            ),
        )
        return attr


def _make_route(feedstock: str, pool: str) -> type[BiomassRoute]:
    name = f"{feedstock}_to_{pool}"
    cls_name = "".join(part.title() for part in name.split("_"))
    return type(
        cls_name,
        (BiomassRoute,),
        {"name": name, "feedstock": feedstock, "pool": pool, "__module__": __name__},
    )


BIOMASS_ROUTE_TECHNOLOGIES = [
    _make_route(feedstock, pool)
    for pool, feedstocks in BIOMASS_ROUTES.items()
    for feedstock in feedstocks
]

#TODO: add pretreatment & transport costs when necessary (e.g. drying, pelletizing)