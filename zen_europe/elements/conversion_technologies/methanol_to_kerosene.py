from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import (
    TechnologyCostDatabase,
)
from zen_europe.datasets.datasets.technology.concawe_fuels import Concawe
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


class MethanolToKerosene(ConversionTechnology):
    """Class containing all data and assumptions for methanol to kerosene
    (dimethyl ether and olefin synthesis, oligomerisation and hydrotreating)."""

    name: str = "methanol_to_kerosene"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of methanol to kerosene to kerosene.
        """
        return Attribute(
            name="reference_carrier", default_value=["kerosene"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of methanol to kerosene to methanol, hydrogen and
        electricity.
        """
        return Attribute(
            name="input_carrier",
            default_value=["methanol", "hydrogen", "electricity"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of methanol to kerosene to kerosene. The source
        allocates the balance to the kerosene, so no co-products are modelled.
        """
        return Attribute(name="output_carrier", default_value=["kerosene"], element=self)

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of methanol to kerosene.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of methanol to kerosene.

        """
        attr = self.conversion_factor
        concawe_dataset = Concawe(source_path=self.source_path)
        cf = concawe_dataset.get_conversion_factor_methanol_to_kerosene()
        source = SourceInformation(
            description=(
                "The conversion factor of methanol to kerosene is taken from Concawe "
                "report 4/24 (Table 116). The balance is allocated to the kerosene, "
                "so no co-products are modelled. The heat output is not modelled."
            ),
            metadata=concawe_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of methanol to kerosene.

        Concawe reports none, so the DEA value of methanol synthesis is used, as
        a comparable chemical conversion plant.
        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                settings=self.settings, source_path=self.source_path
            )
            return tech_db.get_construction_time(
                self, proxy_element_name="methanol_from_hydrogen"
            )
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for methanol to kerosene.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for methanol to
        kerosene.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for methanol to
        kerosene.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_variable(self)

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of methanol to kerosene.

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
        Sets the maximum diffusion rate of methanol to kerosene.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)