from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

from zen_europe.datasets.dataset_collections.ccs_conversion_factor import (
    CCSConversionFactor,
)
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
    ConversionTechnology,
    RetrofittingTechnology,
    SourceInformation,
)


class CHPPostCombustionCCS(RetrofittingTechnology):
    """Base class for CHP plants retrofitted with post-combustion carbon capture
    (CCS). Costs, heat and electricity demand are taken from DEA's
    post-combustion capture retrofit of a 100 MW(th) WtE or biomass CHP plant.
    The capture heat is taken from the plant's district heat output.
    Subclasses only set `name`, `base_technology_name` and, if the fuel already
    contains CO2, `_get_fuel_co2_content`."""

    name: str = "CHP_post_combustion_CCS"
    # intermediate base class: adds no folder level to the output path
    subpath: ClassVar[str] = ""

    def __init__(self, model: Model, power_unit: str = "tCO2/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of CHP CCS to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of CHP CCS to district heat (capture heat taken
        from the CHP plant) and electricity.
        """
        return Attribute(
            name="input_carrier",
            default_value=["district_heat", "electricity"],
            element=self,
        )

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of CHP CCS to carbon.
        """
        return Attribute(name="output_carrier", default_value=["carbon"], element=self)

    def _set_retrofit_reference_carrier(self) -> Attribute:
        """
        Sets the retrofit reference carrier of CHP CCS to carbon.
        """
        return Attribute(
            name="retrofit_reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of CHP CCS.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of CHP CCS.
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
        Return the conversion factor of CHP CCS.

        Values from the DEA technology catalogue for carbon capture, transport
        and storage (Post-combustion carbon capture retrofit - 100 MW(th) WtE
        or biomass CHP plant).
        """
        attr = self.conversion_factor
        dea_dataset = DEA(source_path=self.source_path)
        cf = dea_dataset.get_conversion_factor_CHP_CCS()
        source = SourceInformation(
            description=(
                f"The conversion factor of {self.name} is based on the DEA "
                "technology catalogue for carbon capture, transport and storage "
                "(Post-combustion carbon capture retrofit - 100 MW(th) WtE or "
                "biomass CHP plant). The capture heat is taken from the CHP "
                "plant's district heat output."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for CHP CCS.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for CHP CCS.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for CHP CCS.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path
        )
        return tech_db.get_opex_specific_variable(self)

    def _get_fuel_co2_content(self) -> float:
        """
        CO2 already contained in the fuel [tCO2/MWh fuel], which ends up in the
        flue gas next to the combustion CO2. None for solid fuels.
        """
        return 0.0

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of CHP CCS.

        This factor represents the amount of CO2 captured per unit of
        electricity produced by the CHP plant.
        """
        ccs_cf = CCSConversionFactor(
            settings=self.settings, source_path=self.source_path
        )
        base_tech = cast(
            ConversionTechnology, self.model.elements[self.base_technology_name]
        )
        return ccs_cf.get_retrofit_flow_coupling_factor_CHP_CCS(
            element=self,
            base_tech=base_tech,
            fuel_co2_content=self._get_fuel_co2_content(),
        )

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of CHP CCS.

        The IOGP report assigns carbon capture at biomass power plants to
        `biomass_plant_CCS`, so no existing capacity is assigned here.
        """
        attr = self.capacity_existing
        attr.set_data(
            default_value=0,
            df=None,
            source=AssumptionInformation(
                description=(
                    f"No existing capacity of {self.name} is assumed; carbon capture "
                    "projects at biomass power plants in the IOGP report are assigned "
                    "to biomass_plant_CCS."
                ),
            ),
        )
        return attr

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of CHP CCS.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)

    def _set_capacity_addition_unbounded(self) -> Attribute:
        """
        Sets the unbounded capacity addition of CHP CCS.

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
                    "The unbounded capacity addition of carbon storage is based on the "
                    "median existing and future capacity from the IOGP report, divided "
                    "by the number of nodes in the dataset."
                ),
                metadata=iogp_projects.metadata,
            ),
        )


class BiomassCHPCCS(CHPPostCombustionCCS):
    """Biomass CHP plants retrofitted with post-combustion carbon capture."""

    name: str = "biomass_CHP_CCS"
    base_technology_name: str = "biomass_CHP"


class BiogasCHPCCS(CHPPostCombustionCCS):
    """Biogas CHP engines retrofitted with post-combustion carbon capture. DEA
    has no capture entry for gas engines, so the CHP retrofit is used as a
    proxy."""

    name: str = "biogas_CHP_CCS"
    base_technology_name: str = "biogas_CHP"

    def _get_fuel_co2_content(self) -> float:
        """
        Raw biogas contains CO2 next to the methane, which also ends up in the
        engine flue gas.
        """
        return DEA(source_path=self.source_path).get_co2_content_biogas()