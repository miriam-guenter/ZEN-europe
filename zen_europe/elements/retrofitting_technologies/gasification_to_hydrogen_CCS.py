from __future__ import annotations

from typing import TYPE_CHECKING, cast

from zen_europe.datasets.dataset_collections.technology_cost_database import (
    TechnologyCostDatabase,
)
from zen_europe.datasets.datasets.carrier.ipcc_emission_factors import (
    IPCCEmissionFactors,
)
from zen_europe.datasets.datasets.technology.IOGP_carbon_storage_projects import (
    IOGPCarbonStorageProjects,
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
    RetrofittingTechnology,
    SourceInformation,
)


class GasificationToHydrogenCCS(RetrofittingTechnology):
    """Class containing all data and assumptions for retrofitting hydrogen
    production from biomass gasification with pre-combustion carbon capture."""

    name: str = "gasification_to_hydrogen_CCS"
    base_technology_name: str = "gasification_to_hydrogen"

    def __init__(self, model: Model, power_unit: str = "tCO2/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of gasification to hydrogen CCS to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of gasification to hydrogen CCS to electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["electricity"], element=self
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of gasification to hydrogen CCS to carbon.
        """
        return Attribute(name="output_carrier", default_value=["carbon"], element=self)

    def _set_retrofit_reference_carrier(self) -> Attribute:
        """
        Sets the retrofit reference carrier of gasification to hydrogen CCS to carbon.
        """
        return Attribute(
            name="retrofit_reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of gasification to hydrogen CCS.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of gasification to hydrogen CCS.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                settings=self.settings, source_path=self.source_path
            )
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _get_captured_co2_per_hydrogen(self) -> float:
        """
        Return the CO2 captured per unit of hydrogen output [tCO2/MWh].

        This is the carbon intensity of biomass times the biomass input of the base
        technology per unit of hydrogen and the share of that carbon that is captured.
        """
        ganter_dataset = HydrogenRolloutGanter(source_path=self.source_path)
        ipcc_emission_factors = IPCCEmissionFactors(source_path=self.source_path)
        base_tech = cast(
            ConversionTechnology, self.model.elements[self.base_technology_name]
        )
        conversion_factors = cast(
            list[dict[str, dict[str, float]]], base_tech.conversion_factor.default_value
        )
        biomass_input = next(
            entry["gasif_biomass"]["default_value"]
            for entry in conversion_factors
            if "gasif_biomass" in entry
        )
        return (
            ipcc_emission_factors.data["biomass"]
            * biomass_input
            * ganter_dataset.get_capture_rate_gasification_to_hydrogen()
        )

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of gasification to hydrogen CCS.

        The additional electricity per unit of hydrogen is rebased onto the captured
        CO2, which is what the retrofit is sized by.
        """
        attr = self.conversion_factor
        ganter_dataset = HydrogenRolloutGanter(source_path=self.source_path)
        electricity = (
            ganter_dataset.get_electricity_demand_gasification_to_hydrogen_CCS()
            / self._get_captured_co2_per_hydrogen()
        )
        source = SourceInformation(
            description=(
                "The conversion factor of gasification to hydrogen CCS is the "
                "difference between the electricity balance with and without CCS in "
                "the Supporting Information of Ganter et al. (2024), Table S2, divided "
                "by the CO2 captured per unit of hydrogen."
            ),
            metadata=ganter_dataset.metadata,
        )
        attr.set_data(
            default_value=[
                {"electricity": {"default_value": electricity, "unit": "GWh/kilotCO2"}}
            ],
            source=source,
        )
        return attr

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of gasification to hydrogen CCS.

        This is the CO2 that can be captured per unit of hydrogen output.
        """
        ganter_dataset = HydrogenRolloutGanter(source_path=self.source_path)
        attr = self.retrofit_flow_coupling_factor
        return attr.set_data(
            default_value=self._get_captured_co2_per_hydrogen(),
            unit="tCO2/MWh",
            source=SourceInformation(
                description=(
                    "The retrofit flow coupling factor of gasification to hydrogen CCS "
                    "is the IPCC carbon intensity of biomass times the biomass input "
                    "of the base technology per unit of hydrogen and a capture rate of "
                    "57.4 % (Antonini et al. (2021), Table 3, heat pipe reformer with "
                    "CCS, as used by Ganter et al. (2024))."
                ),
                metadata=ganter_dataset.metadata,
            ),
        )

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for gasification to hydrogen CCS.

        This is the delta between the capex of the CCS-equipped plant and that of the
        base technology, divided by `retrofit_flow_coupling_factor`.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        base_tech = cast(
            ConversionTechnology, self.model.elements[self.base_technology_name]
        )
        return tech_db.get_capex_specific_conversion_retrofit(
            self, base_technology=base_tech
        )

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for gasification to
        hydrogen CCS.

        Like the capex, this is the delta to the base technology, divided by
        `retrofit_flow_coupling_factor`.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        base_tech = cast(
            ConversionTechnology, self.model.elements[self.base_technology_name]
        )
        return tech_db.get_opex_specific_fixed_retrofit(self, base_technology=base_tech)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for gasification to
        hydrogen CCS.

        Ganter et al. (2024) report no variable O&M, so the default is kept.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        return self.opex_specific_variable

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of gasification to hydrogen CCS.

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
        Sets the maximum diffusion rate of gasification to hydrogen CCS.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)

    def _set_capacity_addition_unbounded(self) -> Attribute:
        """
        Sets the unbounded capacity addition of gasification to hydrogen CCS.

        Capacity additions up to the size of a single reference project are
        exempt from the diffusion limit, so that a first plant can be built
        from a zero installed base.
        """
        attr = self.capacity_addition_unbounded
        if not self.settings.investment.use_unbounded_capacity_addition_carbon:
            return attr
        iogp_projects = IOGPCarbonStorageProjects(
            settings=self.settings, source_path=self.source_path
        )
        data = iogp_projects.get_capacity_existing_data()
        median_add = data.median()
        return attr.set_data(
            default_value=median_add,
            unit="tCO2/h",
            source=SourceInformation(
                description=(
                    "The unbounded capacity addition of gasification to hydrogen CCS "
                    "is based on the median existing and future capacity from the IOGP "
                    "report, as for the other CCS retrofits."
                ),
                metadata=iogp_projects.metadata,
            ),
        )
