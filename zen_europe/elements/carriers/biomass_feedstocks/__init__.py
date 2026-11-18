"""Primary biomass feedstocks, one carrier per file."""

from .agri_waste import AgriWaste
from .biomass_feedstock import BiomassFeedstock
from .biowaste import Biowaste
from .forestry_residues import ForestryResidues
from .manure import Manure
from .oil_crops import OilCrops
from .perennial_grasses import PerennialGrasses
from .sludge import Sludge
from .src_crops import SRCCrops
from .starch_crops import StarchCrops
from .stemwood import Stemwood
from .sugar_crops import SugarCrops
from .wood_waste import WoodWaste

BIOMASS_FEEDSTOCKS = [
    # Agriculture
    StarchCrops,
    SugarCrops,
    OilCrops,
    PerennialGrasses,
    SRCCrops,
    Manure,
    AgriWaste,
    # Forestry
    Stemwood,
    ForestryResidues,
    # Waste
    Biowaste,
    WoodWaste,
    Sludge,
]

__all__ = ["BiomassFeedstock", "BIOMASS_FEEDSTOCKS"]
