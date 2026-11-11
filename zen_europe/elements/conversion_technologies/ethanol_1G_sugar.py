from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import (
    TechnologyCostDatabase,
)
from zen_europe.datasets.datasets.financial.dea import DEA
from zen_europe.datasets.datasets.technology.ethanol_sugar_beet_jrc import (
    EthanolSugarBeetJRC,
)
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

# DEA has no data for sugar based ethanol, so its grain based plant is used for
# the costs, the lifetime and the construction time.
_PROXY_TECHNOLOGY = "ethanol_1G_starch"


class Ethanol1GSugar(ConversionTechnology):
    """Class containing all data and assumptions for first generation ethanol
    production by fermentation of sugar from sugar beet."""

    name: str = "ethanol_1G_sugar"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of sugar based ethanol to ethanol.
        """
        return Attribute(name="reference_carrier", default_value=["ethanol"], element=self)

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of sugar based ethanol to sugar crops, natural gas
        (process steam) and electricity.
        """
        return Attribute(
            name="input_carrier",
            default_value=["sugar_crops", "natural_gas", "electricity"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of sugar based ethanol to ethanol and ethanol
        residues (the pressed beet pulp, not dried).
        """
        return Attribute(name="output_carrier", default_value=["ethanol", "ethanol_residues"], element=self)

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of sugar based ethanol, taken from the grain based plant.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self, proxy_element_name=_PROXY_TECHNOLOGY)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of sugar based ethanol.

        """
        jrc_dataset = EthanolSugarBeetJRC(source_path=self.source_path)
        return jrc_dataset.get_conversion_factor_ethanol_1G_sugar(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of sugar based ethanol, taken from the grain
        based plant.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                settings=self.settings, source_path=self.source_path
            )
            return tech_db.get_construction_time(
                self, proxy_element_name=_PROXY_TECHNOLOGY
            )
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for sugar based ethanol,
        taken from the grain based plant.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_capex_specific_conversion(
            self, proxy_element_name=_PROXY_TECHNOLOGY
        )

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for sugar based
        ethanol, taken from the grain based plant.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_fixed(
            self, proxy_element_name=_PROXY_TECHNOLOGY
        )

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for sugar based
        ethanol, taken from the grain based plant.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_variable(
            self, proxy_element_name=_PROXY_TECHNOLOGY
        )

#TODO: add existing capacity for ethanol in the future.
    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of sugar based ethanol.

        """
        attr = self.capacity_existing
        attr.set_data(
            default_value=0,
            df=None,
            source=AssumptionInformation(
                description=("We do not consider existing capacities."),
            ),
        )
        return attr

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of sugar based ethanol.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)

    def _set_capacity_addition_unbounded(self) -> Attribute:
        """
        Sets the unbounded capacity addition of sugar based ethanol.

        Without existing capacity and without other technologies producing
        ethanol, the diffusion limit would never allow a first plant, so
        additions up to the size of one typical plant are exempt from it. The
        size of the DEA grain based plant is used.
        """
        attr = self.capacity_addition_unbounded
        if not self.settings.investment.use_diffusion_rates:
            return attr
        dea_dataset = DEA(source_path=self.source_path)
        return attr.set_data(
            default_value=280,
            unit="MW",
            source=SourceInformation(
                description=(
                    "Capacity additions up to one typical plant are exempt from the "
                    "diffusion limit. The size of the grain based plant (280 MW "
                    "ethanol, DEA technology catalogue for renewable fuels, 105 First "
                    "generation ethanol) is used, as DEA has no sugar based plant."
                ),
                metadata=dea_dataset.metadata,
            ),
        )