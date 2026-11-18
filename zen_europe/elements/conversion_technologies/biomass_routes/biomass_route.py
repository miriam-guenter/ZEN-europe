from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import AssumptionInformation, Attribute, ConversionTechnology


class BiomassRoute(ConversionTechnology):
    """Dummy technology that routes a biomass feedstock 1:1 into a dummy carrier.

    It has no costs and no capacity limits. It only makes the
    feedstock -> technology allocation visible in the results."""

    name: str = "biomass_route"
    subpath: ClassVar[str] = ""
    feedstock: ClassVar[str] = ""
    pool: ClassVar[str] = ""

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_reference_carrier(self) -> Attribute:
        return Attribute(
            name="reference_carrier", default_value=[self.pool], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        return Attribute(
            name="input_carrier", default_value=[self.feedstock], element=self
        )

    def _set_output_carrier(self) -> Attribute:
        return Attribute(name="output_carrier", default_value=[self.pool], element=self)

    def _set_conversion_factor(self) -> Attribute:
        attr = self.conversion_factor
        attr.set_data(
            default_value=[{self.feedstock: {"default_value": 1, "unit": "GWh/GWh"}}],
            source=AssumptionInformation(
                description=(
                    f"Lossless 1:1 routing of {self.feedstock} into {self.pool}."
                )
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


# TODO: add pretreatment & transport costs when necessary (e.g. drying, pelletizing)
