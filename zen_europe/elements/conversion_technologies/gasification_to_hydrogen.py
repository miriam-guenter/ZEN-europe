from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import (
    TechnologyCostDatabase,
)
from zen_europe.datasets.datasets.technology.rollout_hydrogen_ganter import (
    HydrogenRolloutGanter,
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


class GasificationToHydrogen(ConversionTechnology):
    """Class containing all data and assumptions for hydrogen production from
    biomass gasification (indirect steam gasification with a heat pipe reformer,
    followed by water gas shift and pressure swing adsorption)."""

    name: str = "gasification_to_hydrogen"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of gasification to hydrogen to hydrogen.
        """
        return Attribute(
            name="reference_carrier", default_value=["hydrogen"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of gasification to hydrogen to gasification biomass
        and electricity.
        """
        return Attribute(
            name="input_carrier",
            default_value=["gasif_biomass", "electricity"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of gasification to hydrogen to hydrogen.
        """
        return Attribute(
            name="output_carrier", default_value=["hydrogen"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of gasification to hydrogen.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of gasification to hydrogen.

        """
        attr = self.conversion_factor
        ganter_dataset = HydrogenRolloutGanter(source_path=self.source_path)
        cf = ganter_dataset.get_conversion_factor_gasification_to_hydrogen()
        source = SourceInformation(
            description=(
                "The conversion factor of gasification to hydrogen is based on the "
                "Supporting Information of Ganter et al. (2024), Table S2, which uses "
                "the heat pipe reformer case of Antonini et al. (2021). The efficiency "
                "refers to dry biomass."
            ),
            metadata=ganter_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of gasification to hydrogen.

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
        Sets the specific capital expenditure (capex) for gasification to hydrogen.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for gasification to
        hydrogen.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for gasification to
        hydrogen.

        Ganter et al. (2024) report no variable O&M, so the default is kept.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        return self.opex_specific_variable

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of gasification to hydrogen.

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
        Sets the maximum diffusion rate of gasification to hydrogen.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
