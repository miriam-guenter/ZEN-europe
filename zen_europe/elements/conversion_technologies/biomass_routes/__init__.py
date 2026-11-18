"""Dummy technologies routing biomass feedstocks into pools (see SC_charts.drawio)."""

from .agri_waste_to_biomass_slow_pyrolysis import AgriWasteToBiomassSlowPyrolysis
from .agri_waste_to_cellulosic_biomass import AgriWasteToCellulosicBiomass
from .agri_waste_to_dry_biomass_biogas import AgriWasteToDryBiomassBiogas
from .agri_waste_to_solid_biomass import AgriWasteToSolidBiomass
from .biomass_route import BiomassRoute
from .biowaste_to_biomass_slow_pyrolysis import BiowasteToBiomassSlowPyrolysis
from .biowaste_to_wet_biomass_biogas import BiowasteToWetBiomassBiogas
from .codigestion_mix import CoDigestionMix
from .digestate_to_biomass_slow_pyrolysis import DigestateToBiomassSlowPyrolysis
from .digestate_to_solid_biomass import DigestateToSolidBiomass
from .ethanol_residues_to_biomass_slow_pyrolysis import (
    EthanolResiduesToBiomassSlowPyrolysis,
)
from .ethanol_residues_to_wet_biomass_biogas import EthanolResiduesToWetBiomassBiogas
from .forestry_residues_to_biomass_slow_pyrolysis import (
    ForestryResiduesToBiomassSlowPyrolysis,
)
from .forestry_residues_to_solid_biomass import ForestryResiduesToSolidBiomass
from .forestry_residues_to_woody_biomass import ForestryResiduesToWoodyBiomass
from .glycerine_to_wet_biomass_biogas import GlycerineToWetBiomassBiogas
from .manure_to_wet_biomass_biogas import ManureToWetBiomassBiogas
from .oil_crops_to_oily_biomass import OilCropsToOilyBiomass
from .oilseed_meal_to_biomass_slow_pyrolysis import OilseedMealToBiomassSlowPyrolysis
from .oilseed_meal_to_dry_biomass_biogas import OilseedMealToDryBiomassBiogas
from .perennial_grasses_to_biomass_slow_pyrolysis import (
    PerennialGrassesToBiomassSlowPyrolysis,
)
from .perennial_grasses_to_cellulosic_biomass import PerennialGrassesToCellulosicBiomass
from .perennial_grasses_to_dry_biomass_biogas import PerennialGrassesToDryBiomassBiogas
from .perennial_grasses_to_solid_biomass import PerennialGrassesToSolidBiomass
from .pyrolysis_oil_to_oil import PyrolysisOilToOil
from .sludge_to_biomass_slow_pyrolysis import SludgeToBiomassSlowPyrolysis
from .sludge_to_wet_biomass_biogas import SludgeToWetBiomassBiogas
from .src_crops_to_biomass_slow_pyrolysis import SrcCropsToBiomassSlowPyrolysis
from .src_crops_to_solid_biomass import SrcCropsToSolidBiomass
from .src_crops_to_woody_biomass import SrcCropsToWoodyBiomass
from .starch_crops_to_dry_biomass_biogas import StarchCropsToDryBiomassBiogas
from .stemwood_to_biomass_slow_pyrolysis import StemwoodToBiomassSlowPyrolysis
from .stemwood_to_solid_biomass import StemwoodToSolidBiomass
from .stemwood_to_woody_biomass import StemwoodToWoodyBiomass
from .sugar_crops_to_wet_biomass_biogas import SugarCropsToWetBiomassBiogas
from .wet_biomass_biogas_to_biogas_feedstock import WetBiomassBiogasToBiogasFeedstock
from .wood_waste_to_biomass_slow_pyrolysis import WoodWasteToBiomassSlowPyrolysis
from .wood_waste_to_solid_biomass import WoodWasteToSolidBiomass

BIOMASS_ROUTE_TECHNOLOGIES = [
    # -> solid_biomass
    StemwoodToSolidBiomass,
    ForestryResiduesToSolidBiomass,
    SrcCropsToSolidBiomass,
    PerennialGrassesToSolidBiomass,
    AgriWasteToSolidBiomass,
    WoodWasteToSolidBiomass,
    DigestateToSolidBiomass,
    # -> woody_biomass
    StemwoodToWoodyBiomass,
    ForestryResiduesToWoodyBiomass,
    SrcCropsToWoodyBiomass,
    # -> dry_biomass_biogas
    StarchCropsToDryBiomassBiogas,
    PerennialGrassesToDryBiomassBiogas,
    AgriWasteToDryBiomassBiogas,
    OilseedMealToDryBiomassBiogas,
    # -> wet_biomass_biogas
    ManureToWetBiomassBiogas,
    SugarCropsToWetBiomassBiogas,
    BiowasteToWetBiomassBiogas,
    SludgeToWetBiomassBiogas,
    EthanolResiduesToWetBiomassBiogas,
    GlycerineToWetBiomassBiogas,
    # -> cellulosic_biomass
    AgriWasteToCellulosicBiomass,
    PerennialGrassesToCellulosicBiomass,
    # -> oily_biomass
    OilCropsToOilyBiomass,
    # -> biomass_slow_pyrolysis
    StemwoodToBiomassSlowPyrolysis,
    ForestryResiduesToBiomassSlowPyrolysis,
    SrcCropsToBiomassSlowPyrolysis,
    PerennialGrassesToBiomassSlowPyrolysis,
    AgriWasteToBiomassSlowPyrolysis,
    WoodWasteToBiomassSlowPyrolysis,
    BiowasteToBiomassSlowPyrolysis,
    SludgeToBiomassSlowPyrolysis,
    DigestateToBiomassSlowPyrolysis,
    EthanolResiduesToBiomassSlowPyrolysis,
    OilseedMealToBiomassSlowPyrolysis,
    # -> biogas_feedstock
    WetBiomassBiogasToBiogasFeedstock,
    # -> oil
    PyrolysisOilToOil,
]

__all__ = ["BiomassRoute", "CoDigestionMix", "BIOMASS_ROUTE_TECHNOLOGIES"]
