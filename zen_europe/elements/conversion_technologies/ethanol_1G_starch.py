from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.bioenergy_existing_capacity import (
    BioenergyExistingCapacity,
)
from zen_europe.datasets.dataset_collections.technology_cost_database import (
    TechnologyCostDatabase,
)
from zen_europe.datasets.datasets.financial.dea import DEA
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


class Ethanol1GStarch(ConversionTechnology):
    """Class containing all data and assumptions for first generation ethanol
    production by fermentation of starch crops (grain)."""

    name: str = "ethanol_1G_starch"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of first generation ethanol to ethanol.
        """
        return Attribute(name="reference_carrier", default_value=["ethanol"], element=self)

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of first generation ethanol to starch crops,
        natural gas (process heat) and electricity.
        """
        return Attribute(
            name="input_carrier",
            default_value=["starch_crops", "natural_gas", "electricity"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of first generation ethanol to ethanol and
        ethanol residues (the distillers' grains, not dried).
        """
        return Attribute(name="output_carrier", default_value=["ethanol", "ethanol_residues"], element=self)

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of first generation ethanol.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of first generation ethanol.

        """
        attr = self.conversion_factor
        dea_dataset = DEA(source_path=self.source_path)
        cf = dea_dataset.get_conversion_factor_ethanol_1G()
        source = SourceInformation(
            description=(
                "The conversion factor of first generation ethanol is based on the "
                "DEA technology catalogue for renewable fuels (105 First generation "
                "ethanol), normalized to the ethanol output."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of first generation ethanol.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                settings=self.settings, source_path=self.source_path
            )
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for first generation
        ethanol.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for first
        generation ethanol.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for first
        generation ethanol.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_variable(self)

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of first generation ethanol.

        The existing capacity is the Eurostat production capacity for
        biogasoline, of which the starch share is taken from the ePURE
        production statistics.
        """
        if self.settings.investment.use_existing_capacities:
            bioenergy_capacity = BioenergyExistingCapacity(
                settings=self.settings, source_path=self.source_path
            )
            return bioenergy_capacity.get_capacity_existing_ethanol(self)
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
        Sets the maximum diffusion rate of first generation ethanol.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
