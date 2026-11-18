from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute


class BiomassPool(Carrier):
    """Base class for aggregated dummy biomass carriers. They cannot be
    imported and are only supplied by biomass routing technologies."""

    name: str = "biomass_pool"
    # intermediate base class: adds no folder level to the output path
    subpath: ClassVar[str] = ""

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_availability_import(self) -> Attribute:
        """Pools are only filled by routing technologies, never imported."""
        return Attribute(
            "availability_import", default_value=0, element=self, unit=self.power_unit
        )
