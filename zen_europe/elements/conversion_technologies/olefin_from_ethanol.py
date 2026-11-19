from __future__ import annotations

from typing import TYPE_CHECKING, cast

from zen_europe.datasets.datasets.technology.bioethylene_dechema import (
    BioethyleneDECHEMA,
)
from zen_europe.datasets.datasets.technology.bioethylene_irena import BioethyleneIRENA
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import (
    AssumptionInformation,
    Attribute,
    ConversionTechnology,
    SourceInformation,
)


class OlefinFromEthanol(ConversionTechnology):
    """Class containing all data and assumptions for olefin production from
    ethanol (catalytic dehydration of ethanol to ethylene). The ethylene is
    modelled as olefin."""

    name: str = "olefin_from_ethanol"

    def __init__(self, model: Model, power_unit: str = "tproduct/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of olefin from ethanol to olefin.
        """
        return Attribute(
            name="reference_carrier", default_value=["olefin"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of olefin from ethanol to ethanol and natural gas
        (process heat of the endothermic dehydration, as a placeholder for
        industrial heat).
        """
        return Attribute(
            name="input_carrier",
            default_value=["ethanol", "natural_gas"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of olefin from ethanol to olefin.
        """
        return Attribute(name="output_carrier", default_value=["olefin"], element=self)

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of olefin from ethanol.

        """
        attr = self.lifetime
        m_ng = self.model.conversion_technologies["methanol_from_natural_gas"]
        lifetime_methanol = m_ng.lifetime.default_value
        attr.set_data(
            default_value=lifetime_methanol,
            source=SourceInformation(
                description=(
                    "The lifetime of olefin from ethanol is manually set to the "
                    "lifetime of methanol from natural gas, assuming a standard "
                    "industrial technology lifetime (as for the other olefin "
                    "routes)."
                ),
                metadata=cast(SourceInformation, m_ng.lifetime.sources[-1]).metadata,
            ),
        )
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of olefin from ethanol.

        """
        if self.settings.investment.use_construction_times:
            attr = self.construction_time
            m_ng = self.model.conversion_technologies["methanol_from_natural_gas"]
            construction_time_methanol = m_ng.construction_time.default_value
            attr.set_data(
                default_value=construction_time_methanol,
                source=SourceInformation(
                    description=(
                        "The construction time of olefin from ethanol is manually "
                        "set to the construction time of methanol from natural "
                        "gas, assuming a standard industrial construction "
                        "timeline (as for the other olefin routes)."
                    ),
                    metadata=cast(
                        SourceInformation, m_ng.construction_time.sources[-1]
                    ).metadata,
                ),
            )
            return attr
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of olefin from ethanol.

        """
        dataset = BioethyleneDECHEMA(source_path=self.source_path)
        return dataset.get_conversion_factor(self)

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) of olefin from ethanol.

        """
        dataset = BioethyleneIRENA(source_path=self.source_path)
        return dataset.get_capex_specific_conversion(self)

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of olefin from ethanol.

        """
        attr = self.capacity_existing
        attr.set_data(
            default_value=0,
            df=None,
            source=AssumptionInformation(
                description=(
                    "We do not consider existing capacities; ethanol dehydration "
                    "plants are not relevant for today's European ethylene "
                    "production."
                ),
            ),
        )
        return attr

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of olefin from ethanol.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
