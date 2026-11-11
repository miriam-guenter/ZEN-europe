from zen_creator import Sector

from zen_europe.elements.carriers.carbon import Carbon
from zen_europe.elements.conversion_technologies.carbon_storage import CarbonStorage
from zen_europe.elements.conversion_technologies.DAC import DAC
from zen_europe.elements.conversion_technologies.methanol_from_hydrogen import (
    MethanolFromHydrogen,
)
from zen_europe.elements.retrofitting_technologies.BF_BOF_CCS import BF_BOF_CCS
from zen_europe.elements.retrofitting_technologies.biomass_plant_CCS import (
    BiomassPlantCCS,
)
from zen_europe.elements.retrofitting_technologies.cement_post_comb import (
    CementPostComb,
)
from zen_europe.elements.retrofitting_technologies.natural_gas_turbine_CCS import (
    NaturalGasTurbineCCS,
)
from zen_europe.elements.retrofitting_technologies.NG_DRI_CCS import NG_DRI_CCS
from zen_europe.elements.retrofitting_technologies.SMR_CCS import SMR_CCS
from zen_europe.elements.transport_technologies.carbon_pipeline import CarbonPipeline
from zen_europe.elements.retrofitting_technologies.biogas_upgrading_CCS import BiogasUpgradingCCS
from zen_europe.elements.retrofitting_technologies.CHP_CCS import BiogasCHPCCS, BiomassCHPCCS
from zen_europe.elements.retrofitting_technologies.ethanol_CCS import (
    Ethanol1GStarchCCS, Ethanol1GSugarCCS, EthanolCellulosicCCS,
)

from zen_europe.elements.retrofitting_technologies.gasification_to_hydrogen_CCS import (
    GasificationToHydrogenCCS,
)

class CarbonSector(Sector):
    """Carbon capture, transport and storage."""

    name = "carbon"
    required_sectors = ["electricity", "heat"]

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            CarbonStorage,
            CarbonPipeline,
            DAC,
            NaturalGasTurbineCCS,
            BiomassPlantCCS,
            BiogasCHPCCS,
            BiomassCHPCCS,
            SMR_CCS,
            CementPostComb,
            BF_BOF_CCS,
            NG_DRI_CCS,
            MethanolFromHydrogen,
            Carbon,
            BiogasUpgradingCCS,
            Ethanol1GStarchCCS,
            Ethanol1GSugarCCS,
            EthanolCellulosicCCS,
            GasificationToHydrogenCCS,
        ]
