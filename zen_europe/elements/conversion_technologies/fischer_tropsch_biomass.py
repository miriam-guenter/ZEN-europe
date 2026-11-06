from __future__ import annotations

from typing import TYPE_CHECKING

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


class FischerTropschBiomass(ConversionTechnology):
    """Class containing all data and assumptions for biomass gasification
    followed by Fischer-Tropsch synthesis. The liquid products (naphtha, jet fuel
    and diesel) are pooled in the oil carrier."""

    name: str = "fischer_tropsch_biomass"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of biomass Fischer-Tropsch to oil.
        """
        return Attribute(name="reference_carrier", default_value=["oil"], element=self)

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of biomass Fischer-Tropsch to gasification biomass.
        The plant covers its own heat and power demand.
        """
        return Attribute(
            name="input_carrier", default_value=["gasif_biomass"], element=self
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of biomass Fischer-Tropsch to oil and electricity.
        """
        return Attribute(
            name="output_carrier", default_value=["oil", "electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of biomass Fischer-Tropsch.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of biomass Fischer-Tropsch.

        """
        attr = self.conversion_factor
        dea_dataset = DEA(source_path=self.source_path)
        cf = dea_dataset.get_conversion_factor_fischer_tropsch_biomass()
        source = SourceInformation(
            description=(
                "The conversion factor of biomass Fischer-Tropsch is based on the DEA "
                "technology catalogue for renewable fuels (99 Jet fuel from biomass "
                "gasification, 2020 values), normalized to the total liquid output, "
                "which is modelled as oil."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of biomass Fischer-Tropsch.

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
        Sets the specific capital expenditure (capex) for biomass Fischer-Tropsch.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for biomass
        Fischer-Tropsch.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for biomass
        Fischer-Tropsch.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_variable(self)

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of biomass Fischer-Tropsch.

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
        Sets the maximum diffusion rate of biomass Fischer-Tropsch.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)