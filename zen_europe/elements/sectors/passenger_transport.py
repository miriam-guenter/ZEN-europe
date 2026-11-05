from zen_creator import Sector

from zen_europe.elements.carriers.diesel import Diesel
from zen_europe.elements.carriers.gasoline import Gasoline
from zen_europe.elements.carriers.passenger_mileage import PassengerMileage
from zen_europe.elements.conversion_technologies.BEV import BEV
from zen_europe.elements.conversion_technologies.ICE_diesel import ICE_diesel
from zen_europe.elements.conversion_technologies.ICE_petrol import ICE_petrol
from zen_europe.elements.conversion_technologies.FAME import FAME
from zen_europe.elements.conversion_technologies.ethanol_to_gasoline import EthanolToGasoline
from zen_europe.elements.conversion_technologies.HVO_diesel import HVODiesel
from zen_europe.elements.conversion_technologies.methanol_to_gasoline import MethanolToGasoline


class PassengerTransportSector(Sector):
    """Passenger vehicle transport demand."""

    name = "passenger_transport"
    required_sectors = ["electricity"]

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            BEV,
            ICE_diesel,
            ICE_petrol,
            Gasoline,
            Diesel,
            PassengerMileage,
            FAME,
            EthanolToGasoline,
            HVODiesel,
            MethanolToGasoline,
        ]
