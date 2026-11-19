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

from zen_europe.datasets.dataset_collections.heat_demand import HeatDemand
from zen_europe.datasets.datasets.financial.ECB import ECBInflation

# Pelletising of woody biomass for small-scale boilers [EUR/MWh pellets]. PyPSA
# technology-data ("biomass boiler", "pelletizing cost"), an assumption based on
# Visser et al. (2020). 9 EUR/MWh is about 43 EUR/t pellets at 17.3 GJ/t, within 
# the 25-136 EUR/t pelletising costs that Visser et al. found in the literature.
PELLETISING_COST = 9.0
PELLETISING_COST_YEAR = 2019


class BiomassBoiler(ConversionTechnology):
    """Class containing all data and assumptions for biomass boilers."""

    name: str = "biomass_boiler"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of biomass boilers to heat.
        """
        return Attribute(name="reference_carrier", default_value=["heat"], element=self)

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of biomass boilers to the heating biomass pool.
        """
        return Attribute(name="input_carrier", default_value=["woody_biomass"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of biomass boilers to heat.
        """
        return Attribute(name="output_carrier", default_value=["heat"], element=self)

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of biomass boilers.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _get_efficiency(self) -> tuple[float, list[str]]:
        """Return the boiler efficiency in the reference year and its agencies."""
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        eff, agencies = tech_db.get_efficiency(self)
        return eff.loc[self.settings.time.reference_year], agencies

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of biomass boilers.

        """
        attr = self.conversion_factor
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        eff, agencies = self._get_efficiency()
        cf = [{"woody_biomass": {"default_value": 1 / eff, "unit": "GW/GW"}}]
        source = SourceInformation(
            description=(
                "The conversion factor of biomass boilers is based on data from "
                f"{', '.join(agencies)}. "
            ),
            metadata=tech_db.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of biomass boilers.

        """
        if self.settings.investment.use_construction_times:
            attr = self.construction_time
            attr.set_data(
                default_value=0,
                source=AssumptionInformation(
                    description=(
                        "The construction time of biomass boilers is assumed to be 0 "
                        "years."
                    )
                ),
            )
            return attr
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for biomass boilers.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for biomass boilers.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for biomass boilers.

        The boiler data (DEA: automatic stoking, wood pellets or wood chips) assume
        pellets, while ENSPRESO prices woody biomass mostly as chips. Pelletising
        is therefore added per MWh of fuel and rebased onto the heat output with
        the fuel input per MWh heat (1 / efficiency). It is added here rather
        than on the woody_biomass routes, because fast pyrolysis uses the same
        pool without pellets. The share of woody_biomass from roundwood chips and
        pellets (ENSPRESO MINBIOWOOa) is already priced at the gate, so it is
        slightly double counted.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        attr = tech_db.get_opex_specific_variable(self)

        eff, _ = self._get_efficiency()
        price_year = self.settings.time.price_year
        inflation = ECBInflation(source_path=self.source_path).get_inflation_rate(
            base_year=PELLETISING_COST_YEAR, target_year=price_year
        )
        pelletising = PELLETISING_COST * inflation / eff  # Euro/MWh heat
        attr.default_value = attr.default_value + pelletising
        if attr.df is not None:
            attr.df = attr.df + pelletising
        attr.add_source(
            AssumptionInformation(
                description=(
                    f"A pelletising cost of {PELLETISING_COST} "
                    f"EUR{PELLETISING_COST_YEAR}/MWh pellets (PyPSA technology-data, "
                    "'biomass boiler, pelletizing cost', based on Visser et al. 2020, "
                    "doi:10.1016/j.rser.2019.109506; is added, inflated to "
                    f"{price_year} and divided by the boiler efficiency of "
                    f"{eff:.3f}: {pelletising:.2f} Euro/MWh heat."
                )
            )
        )
        return attr

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity for biomass boilers.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        if self.settings.investment.use_existing_capacities:
            heat_demand_dataset = HeatDemand(
                settings=self.settings, source_path=self.source_path
            )
            return heat_demand_dataset.get_capacity_existing(self)
        else:
            attr = self.capacity_existing
            attr.set_data(
                default_value=0,
                df=None,
                source=AssumptionInformation(
                    description=("We do not consider existing capacities."),
                ),
            )
            return attr

    def _set_max_load(self) -> Attribute:
        """
        Sets the maximum load for biomass boilers.

        Returns:
            Attribute: An Attribute object containing the maximum load data.
        """
        heat_demand_dataset = HeatDemand(
            settings=self.settings, source_path=self.source_path
        )

        return heat_demand_dataset.get_max_load(self)

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of biomass boiler.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
