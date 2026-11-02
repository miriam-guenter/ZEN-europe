from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import (
    TechnologyCostDatabase,
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


class BiomassCHP(ConversionTechnology):
    """Class containing all data and assumptions for biomass combined heat and
    power plants (back pressure, wood chips, medium size) supplying district
    heat."""

    name: str = "biomass_CHP"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of biomass CHP plants to electricity, since
        DEA reports their costs per MW of electrical capacity.
        """
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of biomass CHP plants to biomass.
        """
        return Attribute(name="input_carrier", default_value=["comb_biomass"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of biomass CHP plants to electricity and
        district heat.
        """
        return Attribute(
            name="output_carrier",
            default_value=["electricity", "district_heat"],
            element=self,
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of biomass CHP plants.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of biomass CHP plants.

        Both factors are expressed per unit of electricity output: the biomass
        input is 1 / electrical efficiency, and the district heat output is the
        heat efficiency divided by the electrical efficiency.
        """
        attr = self.conversion_factor
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        reference_year = self.settings.time.reference_year
        eff_el, agencies = tech_db.get_efficiency(self)
        eff_th, _ = tech_db.get_efficiency(self, variable="heat_efficiency")
        eff_el = eff_el.loc[reference_year]
        eff_th = eff_th.loc[reference_year]
        cf = [
            {"comb_biomass": {"default_value": 1 / eff_el, "unit": "GWh/GWh"}},
            {"district_heat": {"default_value": eff_th / eff_el, "unit": "GWh/GWh"}},
        ]
        source = SourceInformation(
            description=(
                "The conversion factor of biomass CHP plants is based on the "
                "electrical and heat efficiencies (net, name plate) from "
                f"{', '.join(agencies)}, normalized to the electricity output."
            ),
            metadata=tech_db.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of biomass CHP plants.

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
        Sets the specific capital expenditure (capex) for biomass CHP plants.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for biomass CHP
        plants.

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
        CHP plants.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_variable(self)

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of biomass CHP plants.

        Existing biomass plants from PowerPlantMatching are all assigned to
        `biomass_plant`, so none are assigned here to avoid double counting.
        """
        #TODO: assign existing biomass CHP capacities to this technology and reevaluate capacities assigned to `biomass_plant`
        
        attr = self.capacity_existing
        attr.set_data(
            default_value=0,
            df=None,
            source=AssumptionInformation(
                description=(
                    "Existing biomass capacities are assigned to biomass_plant; "
                    "biomass CHP plants start from zero capacity."
                ),
            ),
        )
        return attr

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of biomass CHP plants.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)