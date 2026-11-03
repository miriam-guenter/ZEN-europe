from __future__ import annotations

from typing import TYPE_CHECKING, cast

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
    RetrofittingTechnology,
    SourceInformation,
)


class BiogasUpgradingCCS(RetrofittingTechnology):
    """Class containing all data and assumptions for capturing the CO2
    off-gas of biogas upgrading, by drying, compressing and liquefying the CO2
    that the upgrading already separates from the methane."""

    name: str = "biogas_upgrading_CCS"
    base_technology_name: str = "biogas_upgrading"

    def __init__(self, model: Model, power_unit: str = "tCO2/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of biogas upgrading CCS to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of biogas upgrading CCS to electricity (for
        drying, compression and liquefaction).
        """
        return Attribute(
            name="input_carrier", default_value=["electricity"], element=self
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of biogas upgrading CCS to carbon.
        """
        return Attribute(name="output_carrier", default_value=["carbon"], element=self)

    def _set_retrofit_reference_carrier(self) -> Attribute:
        """
        Sets the retrofit reference carrier of biogas upgrading CCS to carbon.
        """
        return Attribute(
            name="retrofit_reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of biogas upgrading CCS.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of biogas upgrading CCS.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                settings=self.settings, source_path=self.source_path
            )
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of biogas upgrading CCS.

        """
        attr = self.conversion_factor
        dea_dataset = DEA(source_path=self.source_path)
        cf = dea_dataset.get_conversion_factor_biogas_upgrading_CCS()
        source = SourceInformation(
            description=(
                "The conversion factor of biogas upgrading CCS is the electricity "
                "demand for drying, compressing and liquefying the CO2 from the DEA "
                "technology catalogue for carbon capture, transport and storage "
                "(Liquefaction for biogas plant retrofit)."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of biogas upgrading CCS.

        This is the CO2 that can be captured per unit of upgraded gas: the CO2
        content of the raw biogas times the biogas input of the upgrading per
        unit of output. All CO2 separated by the upgrading is assumed to be
        capturable.
        """
        dea_dataset = DEA(source_path=self.source_path)
        base_tech = cast(
            ConversionTechnology, self.model.elements[self.base_technology_name]
        )
        conversion_factors = cast(
            list[dict[str, dict[str, float]]], base_tech.conversion_factor.default_value
        )
        biogas_input = next(
            entry["biogas"]["default_value"]
            for entry in conversion_factors
            if "biogas" in entry
        )
        attr = self.retrofit_flow_coupling_factor
        return attr.set_data(
            default_value=dea_dataset.get_co2_content_biogas() * biogas_input,
            unit="tCO2/MWh",
            source=SourceInformation(
                description=(
                    "The retrofit flow coupling factor of biogas upgrading CCS is the "
                    "CO2 content of raw biogas from the DEA technology catalogue for "
                    "renewable fuels (Biogas plant, Basic plant, large) times the "
                    "biogas input of biogas upgrading per unit of upgraded gas. All "
                    "CO2 separated by the upgrading is assumed to be capturable."
                ),
                metadata=dea_dataset.metadata,
            ),
        )

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for biogas upgrading CCS.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for biogas
        upgrading CCS.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for biogas
        upgrading CCS.

        DEA reports no variable O&M for the liquefaction; its electricity demand
        is covered by the electricity input.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        return self.opex_specific_variable

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of biogas upgrading CCS.

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
        Sets the maximum diffusion rate of biogas upgrading CCS.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)