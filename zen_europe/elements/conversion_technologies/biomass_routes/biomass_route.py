from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import AssumptionInformation, Attribute, ConversionTechnology

from zen_europe.datasets.datasets.financial.ECB import ECBInflation


class BiomassRoute(ConversionTechnology):
    """Dummy technology that routes a biomass feedstock into a dummy carrier
    (1:1 by default).

    It has no capex and no capacity limits. It makes the feedstock -> technology
    allocation visible in the results. Subclasses can add the conditioning that
    is needed to bring the feedstock into the pool and that is not included in
    the ENSPRESO cost:

    - `pretreatment_steps`: costs per tonne of feedstock (e.g. chipping,
      crushing), converted to a variable opex per MWh of pool output.
    - `feedstock_per_pool`: MWh of feedstock per MWh of pool output, for routes
      that convert the feedstock (e.g. oilseed -> vegetable oil).
    - `byproducts`: co-products per MWh of pool output (e.g. oilseed meal),
      added as output carriers.
    """

    name: str = "biomass_route"
    subpath: ClassVar[str] = ""
    feedstock: ClassVar[str] = ""
    pool: ClassVar[str] = ""

    # Each step: name, cost [EUR/t as received], LHV [GJ/t as received], share of
    # the feedstock energy the step applies to, base year of the cost, source.
    pretreatment_steps: ClassVar[list[dict]] = []
    # MWh feedstock per MWh pool output (1 = lossless routing)
    feedstock_per_pool: ClassVar[float] = 1.0
    # Co-products: {carrier: MWh per MWh of pool output}
    byproducts: ClassVar[dict[str, float]] = {}
    # Source of feedstock_per_pool and byproducts (if not 1:1)
    conversion_description: ClassVar[str] = ""

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
        return Attribute(
            name="output_carrier",
            default_value=[self.pool, *self.byproducts],
            element=self,
        )

    def _set_conversion_factor(self) -> Attribute:
        attr = self.conversion_factor
        cf = [
            {
                self.feedstock: {
                    "default_value": self.feedstock_per_pool,
                    "unit": "GWh/GWh",
                }
            }
        ]
        for carrier, value in self.byproducts.items():
            cf.append({carrier: {"default_value": value, "unit": "GWh/GWh"}})
        if self.conversion_description:
            description = self.conversion_description
        else:
            description = f"Lossless 1:1 routing of {self.feedstock} into {self.pool}."
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(description=description),
        )
        return attr

    def _set_opex_specific_variable(self) -> Attribute:
        """Variable opex of the feedstock conditioning [Euro/MWh pool output].

        Each step's cost [EUR/t feedstock] is divided by the LHV [GJ/t],
        converted to EUR/MWh feedstock, weighted with the energy share it applies
        to, multiplied with the feedstock input per MWh of pool output and
        inflated from its base year to the price year.
        """
        if not self.pretreatment_steps:
            return self.opex_specific_variable
        inflation = ECBInflation(source_path=self.source_path)
        price_year = self.settings.time.price_year
        opex = 0.0
        descriptions = []
        for step in self.pretreatment_steps:
            cost = step["cost"] / step["lhv"] * 3.6 * step["share"]  # EUR/MWh feed
            cost *= self.feedstock_per_pool  # EUR/MWh pool output
            opex += cost * inflation.get_inflation_rate(
                base_year=step["year"], target_year=price_year
            )
            descriptions.append(
                f"{step['name']}: {step['cost']} EUR{step['year']}/t at "
                f"{step['lhv']} GJ/t for {step['share']:.1%} of the feedstock "
                f"({step['source']})"
            )
        attr = self.opex_specific_variable
        attr.set_data(
            default_value=opex,
            unit="Euro/MWh",
            source=AssumptionInformation(
                description=(
                    f"Conditioning of {self.feedstock} into {self.pool} that is not "
                    "included in the ENSPRESO cost, per MWh of pool output and "
                    "inflated to the price year. " + "; ".join(descriptions) + "."
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


# TODO: add pretreatment for further feedstocks, storage & transport when necessary
