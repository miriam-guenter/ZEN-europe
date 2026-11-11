from zen_creator import Sector

from zen_europe.elements.carriers.biomass_feedstocks import BIOMASS_FEEDSTOCKS
from zen_europe.elements.carriers.biomass_pools import BIOMASS_POOLS
from zen_europe.elements.conversion_technologies.biomass_routes import (
    BIOMASS_ROUTE_TECHNOLOGIES, CoDigestionMix
)
from zen_europe.elements.conversion_technologies.anaerobic_digestion import AnaerobicDigestion
from zen_europe.elements.carriers.biogas import Biogas
from zen_europe.elements.carriers.digestate import Digestate
from zen_europe.elements.conversion_technologies.biogas_upgrading import (
    BiogasUpgrading,
)
from zen_europe.elements.retrofitting_technologies.biogas_upgrading_CCS import (
    BiogasUpgradingCCS,
)
from zen_europe.elements.conversion_technologies.biogas_CHP import BiogasCHP
from zen_europe.elements.conversion_technologies.biomass_CHP import BiomassCHP
from zen_europe.elements.retrofitting_technologies.CHP_CCS import (
    BiogasCHPCCS, BiomassCHPCCS
)
from zen_europe.elements.conversion_technologies.pyrolysis_fast import FastPyrolysis
from zen_europe.elements.conversion_technologies.pyrolysis_slow import SlowPyrolysis
from zen_europe.elements.carriers.pyrolysis_oil import PyrolysisOil
from zen_europe.elements.conversion_technologies.FAME import FAME
from zen_europe.elements.carriers.ethanol import Ethanol
from zen_europe.elements.conversion_technologies.ethanol_1G_starch import Ethanol1GStarch
from zen_europe.elements.conversion_technologies.ethanol_cellulosic import (
    EthanolCellulosic,
)
from zen_europe.elements.retrofitting_technologies.ethanol_CCS import (
    Ethanol1GStarchCCS,
    EthanolCellulosicCCS,
)
from zen_europe.elements.conversion_technologies.ethanol_to_gasoline import EthanolToGasoline
from zen_europe.elements.conversion_technologies.HVO_diesel import HVODiesel
from zen_europe.elements.conversion_technologies.HVO_jet import HVOJet
from zen_europe.elements.conversion_technologies.fischer_tropsch_biomass import FischerTropschBiomass

class BiomassSector(Sector):
    """Biomass supply: primary feedstocks with ENSPRESO potentials, the pooled
    (dummy) carriers per use pathway, and the dummy technologies routing each
    feedstock into its pools."""

    name = "biomass"
    required_sectors = ["electricity", "heat", "gas", "district_heating", "refining"]

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            *BIOMASS_FEEDSTOCKS,
            *BIOMASS_POOLS,
            *BIOMASS_ROUTE_TECHNOLOGIES,
            CoDigestionMix,
            AnaerobicDigestion,
            BiogasUpgrading,
            Biogas,
            Digestate,
            BiogasUpgradingCCS,
            BiogasCHP,
            BiomassCHP,
            BiogasCHPCCS,
            BiomassCHPCCS,
            PyrolysisOil,
            FastPyrolysis,
            SlowPyrolysis,
            FAME,
            Ethanol,
            Ethanol1GStarch,
            EthanolCellulosic,
            Ethanol1GStarchCCS,
            EthanolCellulosicCCS,
            EthanolToGasoline,
            HVODiesel,
            HVOJet,
            FischerTropschBiomass,
        ]