from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from zen_europe.datasets.dataset_collections.technology_cost_database import (
    TechnologyCostDatabase,
)
from zen_europe.datasets.datasets.financial.dea import DEA
from zen_europe.datasets.datasets.technology.IOGP_carbon_storage_projects import (
    IOGPCarbonStorageProjects,
)
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import (
    AssumptionInformation,
    Attribute,
    RetrofittingTechnology,
    SourceInformation,
)

# Costs, lifetime and construction time are taken from the liquefaction of the
# (already separated) CO2 of biogas upgrading, since fermentation CO2 is nearly
# pure as well and only needs drying, compression and liquefaction.
_PROXY_TECHNOLOGY = "biogas_upgrading_CCS"


class FermentationCCS(RetrofittingTechnology):
    """Base class for capturing the nearly pure fermentation CO2 of ethanol
    plants by drying, compressing and liquefying it. Costs and electricity
    demand are taken from DEA's liquefaction for biogas plants as a proxy."""

    name: str = "fermentation_CCS"
    # intermediate base class: adds no folder level to the output path
    subpath: ClassVar[str] = ""

    def __init__(self, model: Model, power_unit: str = "tCO2/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of fermentation CCS to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of fermentation CCS to electricity (for drying,
        compression and liquefaction).
        """
        return Attribute(
            name="input_carrier", default_value=["electricity"], element=self
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of fermentation CCS to carbon.
        """
        return Attribute(name="output_carrier", default_value=["carbon"], element=self)

    def _set_retrofit_reference_carrier(self) -> Attribute:
        """
        Sets the retrofit reference carrier of fermentation CCS to carbon.
        """
        return Attribute(
            name="retrofit_reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of fermentation CCS, from the biogas liquefaction
        proxy.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self, proxy_element_name=_PROXY_TECHNOLOGY)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of fermentation CCS, from the biogas
        liquefaction proxy.

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

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of fermentation CCS.

        This is the electricity demand for drying, compressing and liquefying
        the fermentation CO2, from DEA's liquefaction for biogas plants.
        """
        attr = self.conversion_factor
        dea_dataset = DEA(source_path=self.source_path)
        cf = dea_dataset.get_conversion_factor_biogas_upgrading_CCS()
        source = SourceInformation(
            description=(
                f"The conversion factor of {self.name} is the electricity demand "
                "for drying, compressing and liquefying CO2 from the DEA technology "
                "catalogue for carbon capture, transport and storage (Liquefaction "
                "for biogas plant retrofit), used as a proxy since fermentation CO2 "
                "is nearly pure."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of fermentation CCS.

        This is the fermentation CO2 that can be captured per unit of ethanol,
        the reference carrier of the base technology.
        """
        dea_dataset = DEA(source_path=self.source_path)
        attr = self.retrofit_flow_coupling_factor
        return attr.set_data(
            default_value=dea_dataset.get_co2_from_ethanol_fermentation(),
            unit="tCO2/MWh",
            source=AssumptionInformation(
                description=(
                    f"The retrofit flow coupling factor of {self.name} is the CO2 "
                    "released by fermentation per unit of ethanol from the "
                    "stoichiometry (0.957 tCO2 per ton of ethanol, 26.9 GJ/ton). It is "
                    "an upper bound for the recoverable fermentation CO2."
                ),
            ),
        )

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for fermentation CCS,
        from the biogas liquefaction proxy.

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
        Sets the specific fixed operational expenditure (opex) for fermentation
        CCS, from the biogas liquefaction proxy.

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
        Sets the specific variable operational expenditure (opex) for
        fermentation CCS.

        DEA reports no variable O&M for the liquefaction; its electricity demand
        is covered by the electricity input.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        return self.opex_specific_variable

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of fermentation CCS.

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
        Sets the maximum diffusion rate of fermentation CCS.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)

    def _set_capacity_addition_unbounded(self) -> Attribute:
        """
        Sets the unbounded capacity addition of fermentation CCS.

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
                    f"The unbounded capacity addition of {self.name} is based on the "
                    "median existing and future capacity from the IOGP report, as for "
                    "the other CCS retrofits."
                ),
                metadata=iogp_projects.metadata,
            ),
        )


class Ethanol1GStarchCCS(FermentationCCS):
    """Capture of the fermentation CO2 of first generation ethanol."""

    name: str = "ethanol_1G_starch_CCS"
    base_technology_name: str = "ethanol_1G_starch"


class EthanolCellulosicCCS(FermentationCCS):
    """Capture of the fermentation CO2 of cellulosic ethanol. The CO2 from
    burning the lignin residue is not captured."""

    name: str = "ethanol_cellulosic_CCS"
    base_technology_name: str = "ethanol_cellulosic"
