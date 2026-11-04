from __future__ import annotations

import re
import urllib.request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pandas as pd
import numpy as np
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

from zen_europe.datasets.datasets.financial._cost_schema import (
    CO2_BASIS_UNITS,
    INDEX_NAMES,
    VALUE_COLUMNS,
)
from zen_europe.settings.cache import get_active_cache_settings
from zen_europe.utils.constants import Constants

# internal technology name -> DEA (Technology, category, input, size) row key.
# `size=None` means the technology varies by plant_size in the source data
# (looked up dynamically); a fixed string means the technology only exists at
# that one DEA size.


_MAIN_TECHS: dict[str, tuple[str, str, str, str | None]] = {
    "wind_onshore": (
        "Onshore wind turbine, utility",
        "renewable power",
        "wind",
        "large",
    ),
    "photovoltaics": (
        "PV",
        "renewable power",
        "solar",
        "utility-scale, ground mounted",
    ),
    "rooftop_photovoltaics": ("PV", "renewable power", "solar", "residential rooftop"),
    "rooftop_photovoltaics_com": (
        "PV",
        "renewable power",
        "solar",
        "commercial/industrial rooftop",
    ),
    "natural_gas_turbine": (
        "Gas turbine, combined cycle",
        "extraction",
        "natural gas",
        "large",
    ),
    "oc_natural_gas_turbine": (
        "Gas turbine, open cycle",
        "back pressure",
        "natural gas",
        "medium",
    ),
    "hard_coal_plant": (
        "Coal power plant, supercritical",
        "extraction",
        "coal",
        "medium",
    ),
    "natural_gas_boiler_DH": ("Gas boiler", "boiler", "natural gas", "medium"),
    "heat_pump_DH": ("Heat pump, air source", "heat pump", "electricity", None),
    "waste_boiler_DH": ("Waste boiler", "boiler", "waste", "small"),
    "biomass_boiler_DH": ("Biomass boiler", "boiler", "wood chips", "medium"),
    "biomass_CHP": ("Biomass CHP", "back pressure", "wood chips", "medium"),
    "electrode_boiler_DH": ("Electric boiler", "boiler", "electricity", None),
    "fuel_cell": ("Low temp PEM fuel cell", "back pressure", "hydrogen", "small"),
}

# DEA reports rooftop-residential/rooftop-commercial/utility-scale PV as three separate
# `Technology` rows, keyed here via `_SIZE_MAP_PV` purely to find each one's DEA label
# -- unlike
# `_MAIN_TECHS`'s other `fixed_size` entries, this isn't a real small/medium/large
# *capacity*
# split, since each of the three is already its own internal technology name. None of
# them have
# genuine size variation, so (per `_cost_schema`'s "agencies/technologies without a size
# dimension report under 'M'" convention, followed by every other agency here) their
# rows are
# tagged `plant_size="M"` regardless of which DEA label matched -- see `_parse_main`.
_PV_TECHS = {"photovoltaics", "rooftop_photovoltaics", "rooftop_photovoltaics_com"}
_SIZE_MAP = {"S": "small", "M": "medium", "L": "large"}
_SIZE_MAP_PV = {
    "S": "residential rooftop",
    "M": "commercial/industrial rooftop",
    "L": "utility-scale, ground mounted",
}

# `heat_pump_DH`'s DEA label now carries a DH-supply-temperature suffix (a 2025
# catalogue
# revision split district-heating heat pumps by heat source x size x supply temperature,
# where
# there used to be one entry per size); we use the 70/35 degree, air-source variant, the
# closest
# continuation of the old single "Heat pump, air source" entry.
_LABEL_SUFFIXES: dict[str, str] = {
    "heat_pump_DH": " - dh temp 70/35 degrees",
}

# Technologies whose DEA `Technology` label no longer decomposes into the standard
# Type/Category/Input/Size join used by `_MAIN_TECHS`: a catalogue revision restructured
# offshore wind into a grid-connection x foundation-type taxonomy with no separate size
# field
# (replacing the old single "Offshore wind turbines"/".... nearshore" entries). Internal
# technology name -> (complete DEA `Technology` label, plant_size it represents). We use
# the
# AC-connected, fixed-bottom variant for both -- standard grid-connected offshore wind
# on a
# fixed-bottom foundation, still the dominant real-world technology and the closest
# continuation
# of the old entries -- always at plant_size "L", matching their old fixed "large" size.
_MAIN_TECHS_LITERAL: dict[str, tuple[str, str]] = {
    "wind_offshore": ("Offshore Wind - AC connected - Fixed bottom", "L"),
    "wind_offshore_near_shore": ("Nearshore Wind - AC connected - Fixed bottom", "L"),
}

# internal technology name -> DEA (technology label, building age) row key,
# for the individual (residential) heating installations dataset.
_IH_TECHS: dict[str, tuple[str, str]] = {
    "natural_gas_boiler": ("Natural gas boiler", "existing building"),
    "heat_pump": ("Heat pump, Air-to-water", "existing building"),
    "oil_boiler": ("Oil boiler (mineral oil fired, < 10 % FAME)", "existing building"),
    "biomass_boiler": (
        "Biomass boiler, automatic stoking , wood pellets or wood chips",
        "existing building",
    ),
    "electrode_boiler": ("Electric heating", "new building"),
}
# DEA has no "small" building-level entry; only single-family houses (M) and
# apartment complexes (L) are reported.
_IH_SIZE_MAP = {"M": "single-family house", "L": "apartment complex"}

_SCENARIOS = {"min": "lower", "max": "upper", "ref": "ctrl"}
_COST_VAR_LABELS = {
    "capex": "Nominal investment",
    "fopex": "Fixed O&M",
    "vopex": "Variable O&M",
}

# internal technology name -> DEA carbon-capture technology row key. Costs are
# reported per tCO2/h captured rather than per kW, so these use
# `CO2_BASIS_UNITS` instead of the power/heat schema.
_CCS_TECHS: dict[str, str] = {
    "DAC": "Solid Adsorption Direct Air Capture Plant",
    "cement_post_comb": (
        "Post-combustion carbon capture - Retrofit 4500 ton clinker per day cement kiln"
    ),
    "NG_DRI_CCS": (
        "Post-combustion carbon capture - Retrofit 4500 ton clinker per day cement kiln"
    ),
    "BF_BOF_CCS": (
        "Post-combustion carbon capture - Retrofit 4500 ton clinker per day cement kiln"
    ),
    "SMR_CCS": (
        "Post-combustion carbon capture retrofit - 100 MW(th) WtE or biomass CHP plant"
    ),
    "biogas_upgrading_CCS": "Liquefaction for biogas plant retrofit",
}
# DAC has no reported variable O&M figure.
_CCS_COST_PARS: dict[str, dict[str, str]] = {
    "DAC": {
        "capex": "Specific investment [mill €/(tCO2/hour)] (CO2 output)",
        "fopex": "Fixed O&M [mill €/(tCO2/hour)]",
    },
    "_default": {
        "capex": "Specific investment [mill €/[tCO2/hour]] (CO2 output)",
        "fopex": "Fixed O&M [mill €/[tCO2/hour]] (CO2 output)",
        "vopex": "Variable O&M [€/tCO2] (CO2 output)",
    },
    "biogas_upgrading_CCS": {
        "capex": "Investment Compression & Liquefaction - 2 t CO₂/h [mill €/(tLCO2/h)]",
        "fopex": "Fixed O&M 2 t CO₂/h [mill €/(tCO2/hour)] (CO2 output)",
    },
}
_CCS_SCENARIOS = {"min": "Lower", "max": "Upper", "ref": "Est"}

# DEA's own stable media links for the four source workbooks (the legacy script's
# ens.dk/sites/ens.dk/files/... URLs no longer resolve), and the local filename each is
# cached
# under on first load (matching the other agencies' checked-in-raw-file convention).
# Each
# workbook contains an "alldata_flat" sheet.
_SOURCES: dict[str, tuple[str, str]] = {
    "main": (
        "technology_data_for_el_and_dh.xlsx",
        "https://ens.dk/media/8615/download",
    ),
    "ih": (
        "technology_data_heating_installations.xlsx",
        "https://ens.dk/media/8518/download",
    ),
    "rf": (
        "data_sheets_for_renewable_fuels.xlsx",
        "https://ens.dk/media/6444/download",
    ),
    "ccs": (
        "technology_data_for_carbon_capture_transport_storage.xlsx",
        "https://ens.dk/media/5729/download",
    ),
    "dh_transport": (
        "technology_data_for_energy_transport.xlsx",
        "https://ens.dk/media/7681/download",
    ),
}

_REQUIRED_SOURCE_COLUMNS = {
    "ws",
    "Technology",
    "cat",
    "par",
    "unit",
    "priceyear",
    "est",
    "year",
    "val",
}

# `ws`-sheet name (within the energy-transport workbook's `alldata_flat`) for each
# district
# heating distribution network variant -> our area-type label. DEA also reports DH
# *transmission* (bulk, inter-node pipelines, sheet "3.1 DH transmission", `€/MW/m`
# capex tiered
# by capacity band) in the same workbook, not extracted here: `district_heating_grid` is
# a
# `ConversionTechnology` (district_heat -> heat), matching the last-mile distribution
# step, not
# bulk transport between nodes.
_DH_DISTRIBUTION_SHEETS: dict[str, str] = {
    "suburban": "3.2 DH_Distribu Suburb",
    "city": "3.3 DH_Distribu City",
    "new_area": "3.4 DH_Distribu New area",
}
# DH distribution capex is reported per km² of network service area (not per kW, unlike
# every
# other DEA figure in this file), so it doesn't fit `_cost_schema`'s Euro/kW convention;
# fopex
# and vopex are capacity/energy-based and would fit, but are kept in the same
# native-unit table
# for consistency. `get_dh_distribution_data` returns this separately from `get_costs()`
# rather
# than forcing it into the shared schema -- how to turn an area-based network cost into
# a
# technology capex is a modeling decision for whatever consumes it, not this dataset.
_DH_DISTRIBUTION_COST_PARS: dict[str, str] = {
    "capex": "Investments cost, distribution network  [M€/km2]",
    "fopex": "Fixed O&M [€/MW/year]",
    "vopex": "Variable O&M [€/MWh]",
}
_DH_DISTRIBUTION_TECH_PARS: dict[str, str] = {
    "lifetime": "Technical life time [years]",
    "construction_time": "Construction time [years]",
    "energy_losses": "Energy losses, network [%]",
}

# The energy-transport workbook's `priceyear` column is blank (like `rf`/`ih`); its
# Index sheet
# states the price basis instead: "Cost data for el transmission, DH, H2 pipelines and
# road is
# in 2025 EURO".
_DH_MONEY_YEAR_SRC = 2025
_DH_DISTRIBUTION_INDEX_NAMES = ["area_type", "variable", "scenario", "year"]
_DH_DISTRIBUTION_VALUE_COLUMNS = [
    "value",
    "unit",
    "money_year_src",
    "value_src",
    "unit_src",
]

# internal technology name -> DEA renewable-fuel technology row key. All
# reported on a Euro/kW(h)-of-output basis, so they fit the power/heat schema
# once converted; (par_string, multiplier_to_schema_unit) per technology and
# variable. `fischer_tropsch`'s "Fixed O&M" figure is priced per MWh of
# output rather than per MW/year of capacity (looks like a unit labeling
# error in the source spreadsheet, still present in the current catalogue)
# and `electrolysis`'s old "Fixed O&M" figure was a percentage of capex per
# year rather than an absolute figure -- both are left out, as the legacy
# script did. `electrolysis`'s "Variable O&M" figure is no longer reported
# at all in the current catalogue, so vopex is left out for it too.
_RF_TECHS: dict[str, str] = {
    "methanol_from_biomass": "Bio Methanol",
    "methanol_from_hydrogen": "Methanol from hydrogen and carbon dioxide",
    "haber_bosch": (
        "Green Ammonia plant: Hydrogen to ammonia (excl. electrolyzer and excl. ASU)"
    ),
    "fischer_tropsch": "Hydrogen to Jet Fuel",
    # DEA reorganized its old single "Slow pyrolysis ... from straw" entry into scale x
    # feedstock variants (large/small scale x straw/garden waste/digestate); we use the
    # large-scale, straw-feedstock variant, the closest continuation of the old entry.
    "pyrolysis_slow": "Large scale slow pyrolysis (20 MW) - Straw feedstock",
    "pyrolysis_fast": "Fast pyrolysis (25 MW) - Wood feedstock",
    "methanation": "SNG from Biogas", # change this (get technology data from other source)
    "biogas_methanation": "SNG from Biogas",
    "gasification": "Gasifier, biomass, bio-SNG, medium - large scale",
    "electrolysis": "Hydrogen production via PEMEC electrolysis for 100 MW plant",
    "anaerobic_digestion": "Biogas plant, Basic plant, large [~ 6,000 Nm3 CH4/h]",
    "biogas_upgrading": "Biogas upgrading - Amine scrubber [~6,000 Nm3 CH4/h)",
    "methanol_from_biogas": "Methanol from biogas and hydrogen",
    "FAME": "Vegetable Oil FAME",
    "ethanol_1G_starch": "1st Generation Ethanol",
    "ethanol_cellulosic": "Cellulosic Ethanol",
    "HVO_jet": "HVO Jet Fuel",
    "HVO_diesel": "HVO / renwable diesel",
}
_RF_COST_PARS: dict[str, dict[str, tuple[str, float]]] = {
    "methanol_from_biomass": {
        "capex": ("Specific investment [M€/MW Methanol]", 1000.0),
        "fopex": ("Fixed O&M [M€/MW/year Methanol]", 1000.0),
        "vopex": ("Variable O&M [€/MWh methanol]", 1.0),
    },
    "methanol_from_hydrogen": {
        "capex": ("Specific investment [M€/MW-methanol]", 1000.0),
        "fopex": ("Fixed O&M [k€/[MW-methanol/year]]", 1.0),
        "vopex": ("Variable O&M [€/MWh-methanol]", 1.0),
    },
    "haber_bosch": {
        "capex": ("Specific investment [M€/MW Ammonia output]", 1000.0),
        "fopex": ("Fixed O&M [k€/MW Ammonia/year]", 1.0),
        "vopex": ("Variable O&M [€/MWh Ammonia]", 1.0),
    },
    "fischer_tropsch": {
        "capex": ("Specific investment [M€/MW Liquids/year]", 1000.0),
        "vopex": ("Variable O&M [€/MWH Liquids]", 1.0),
    },
    # DEA's reorganized pyrolysis chapter merged fixed and variable O&M into a single
    # per-MW/year figure (previously reported separately); mapped to fopex only, vopex
    # is left
    # unset rather than guessing a split.
    "pyrolysis_slow": {
        "capex": ("Specific investment [M€/MW output from pyrolysis process]", 1000.0),
        "fopex": (
            "Fixed and variabel O&M [M€/MW output from pyrolysis process/year]",
            1000.0,
        ),
    },
    "pyrolysis_fast": {
        "capex": ("Specific investment [M€/MW output from pyrolysis process]", 1000.0),
        "fopex": (
            "Fixed and variable O&M [M€/MW output from pyrolysis process/year]",
            1000.0,
        ),
    },
    "methanation": {
        "capex": ("Specific investment [M€/MW SNG]", 1000.0),
        "fopex": ("Fixed O&M [M€/MW/year SNG]", 1000.0),
        "vopex": ("Variable O&M [€/MWh SNG]", 1.0),
    },
    "biogas_methanation": {
        "capex": ("Specific investment [M€/MW SNG]", 1000.0),
        "fopex": ("Fixed O&M [M€/MW/year SNG]", 1000.0),
        "vopex": ("Variable O&M [€/MWh SNG]", 1.0),
    },
    "gasification": {
        "capex": ("Specific investment [M€/MWth]", 1000.0),
        "fopex": ("Fixed O&M [€/MWth/year]", 1 / 1000),
        "vopex": ("Variable O&M [€/MWhth]", 1.0),
    },
    "electrolysis": {
        "capex": ("Specific investment [€/kW of total input_e]", 1.0),
        # no separate "Variable O&M" figure is reported for this technology any more.
    },
    "anaerobic_digestion": {
        # relabeled "MWh Output" in the current catalogue, but the values (order of
        # magnitude
        # ~1 M€/MW) confirm this is still a capacity, not an annual-output, basis --
        # almost
        # certainly a labeling inconsistency in DEA's own spreadsheet, not a methodology
        # change.
        "capex": ("Specific investment [M€/MWh Output]", 1000.0),
        # combined fixed+variable O&M, now reported directly on a €/MW/year capacity
        # basis --
        # replaces the old separate ton-input-based fopex figure (which needed an
        # empirical
        # €/(ton/year) -> €/kW/year conversion factor) and the old vopex figure, both
        # gone from
        # the current catalogue; mapped to fopex only, vopex is left unset.
        "fopex": ("Total O&M [k€/MW/year]", 1.0),
    },
    "biogas_upgrading": {
        "capex": (
            "Specific investment, upgrading and methane reduction [k€/MW output]",
            1.0,
        ),
        "fopex": (
            "- of which fixed O&M costs upgrading and methane reduction, "
            "excl. electricity and heat [k€/MW output/year]",
            1.0,
        ),
        "vopex": ("Variable O&M [€/GJ output]", Constants.GJ_PER_MWH),
    },
    "methanol_from_biogas": {
        "capex": ("Specific investment [M€/MW-methanol]", 1000.0),
        "fopex": ("Fixed O&M [k€/[MW-methanol/year]]", 1.0),
        "vopex": ("Variable O&M [€/MWh-methanol]", 1.0),
    },
     "FAME": {
        "capex": ("Specific investment [M €/MW]", 1000.0),
        "fopex": ("Fixed O&M [M €/MW/year]", 1000.0),
        "vopex": ("Variable O&M [€/MWh]", 1.0),
    },
    "ethanol_1G_starch": {
        "capex": ("Specific investment [M€/MW Ethanol]", 1000.0),
        "fopex": ("Fixed O&M [M€/MW/year]", 1000.0),
        "vopex": ("Variable O&M [€/MWh]", 1.0),
    },
    # DEA labels the variable O&M "[€/MW Ethanol]", but its per-ton figure
    # confirms it is per MWh of ethanol.
    "ethanol_cellulosic": {
        "capex": ("Specific investment [M€/MW Ethanol]", 1000.0),
        "fopex": ("Fixed O&M [M€/MW/year Ethanol]", 1000.0),
        "vopex": ("Variable O&M [€/MW Ethanol]", 1.0),
    },
        "HVO_jet": {
        "capex": ("Specific investment [M €/MW HVO Jet]", 1000.0),
        "fopex": ("Fixed O&M [M €/MW/year]", 1000.0),
        "vopex": ("Variable O&M [€/MWh]", 1.0),
    },
    "HVO_diesel": {
        "capex": ("Specific investment [M €/MW]", 1000.0),
        "fopex": ("Fixed O&M [M €/MW/year]", 1000.0),
        "vopex": ("Variable O&M [€/MWh]", 1.0),
    },
}

# Renewable-fuel cost variables that only use a share of the reported figure:
# (technology, variable) -> (par of the share, par of the total), both reported
# by DEA on the same per-ton basis. The share is applied per estimate and year.
# DEA's "Total O&M" of biogas plants includes the plant's own electricity and
# heat, which the model already charges through the input carriers, so only the
# O&M excluding electricity and heat is kept.
_RF_COST_SHARES: dict[tuple[str, str], tuple[str, str]] = {
    ("anaerobic_digestion", "fopex"): (
        "- of which O&M, excl electricity and heat [€/(ton input/year)]",
        "Total O&M [€/(ton input/year)]",
    ),
}

# Renewable-fuel technologies whose "Lower"/"Upper" estimates are reported as
# factors on the central estimate ("ctrl") rather than as absolute values
# (e.g. 0.5 / 1.5 for the investment, 0.9 / 1.1 for O&M). They are converted to
# absolute values before use.
_RF_RELATIVE_BOUNDS_TECHS = {
    "methanol_from_biomass",
    "methanol_from_hydrogen",
    "methanol_from_biogas",
    "fischer_tropsch",
    "methanation",
    "biogas_methanation",
    "FAME",
    "ethanol_1G_starch",
    "ethanol_cellulosic",
    "HVO_jet",
    "HVO_diesel",
}

_RF_SCENARIOS_DEFAULT = {"min": "Lower", "max": "Upper", "ref": "ctrl"}
# anaerobic_digestion/biogas_upgrading use "Est" for the reference
# scenario where every other DEA renewable-fuel technology uses "ctrl" -- the
# legacy script always looked for "ctrl" and so silently never found a
# reference-scenario value for these two technologies; ported correctly here.
# _RF_SCENARIOS_ALT = {"min": "Lower", "max": "Upper", "ref": "Est"}
# _RF_ALT_SCENARIO_TECHS = {"anaerobic_digestion", "biogas_upgrading"}

# The renewable-fuels workbook's `priceyear` column is entirely blank (unlike the other
# three
# DEA workbooks); its own Index sheet states the price basis instead: "All cost data is
# in 2020
# EURO, except the chapters on pyrolysis which are in 2025 EURO".
_RF_MONEY_YEAR_SRC: dict[str, int] = {"pyrolysis_slow": 2025, "pyrolysis_fast": 2025}
_RF_DEFAULT_MONEY_YEAR_SRC = 2020


def _dea_size(plant_size: str, technology: str) -> str:
    return (
        _SIZE_MAP_PV[plant_size] if technology in _PV_TECHS else _SIZE_MAP[plant_size]
    )


def _convert_main_unit(unit_src: str, variable: str) -> float:
    """Multiplier from a DEA source unit to this package's standard unit."""
    if variable == "capex" and unit_src in ("MEUR/MW_e", "MEUR/MW_h"):
        return 1000.0  # MEUR/MW -> EUR/kW
    if variable == "fopex" and unit_src in ("EUR/MW_e/y", "EUR/MW_h/y"):
        return 1 / 1000  # EUR/MW/y -> EUR/kW/year
    if variable == "vopex" and unit_src in ("EUR/MWh_e", "EUR/MWh_h"):
        return 1.0  # already EUR/MWh
    raise ValueError(f"Unexpected DEA unit '{unit_src}' for variable '{variable}'")


def _convert_ccs_unit(unit_src: str, variable: str) -> float:
    """Multiplier from a DEA carbon-capture source unit to `CO2_BASIS_UNITS`.

    Source unit strings are inconsistently written across technologies
    (`millEUR/(tCO2/hour)`, `millEUR/[tCO2/hour`, `millEUR/(tLCO2/h)` for liquid
    CO2), so this matches on normalized substrings rather than exact strings.
    """
    normalized = (
        unit_src.lower()
        .replace(" ", "")
        .replace("tlco2", "tco2")
        .replace("tco2/hour", "tco2/h")
    )
    multiplier = 1e6 if "mill" in normalized else 1.0
    if variable in ("capex", "fopex") and "tco2/h" in normalized:
        return multiplier
    if variable == "vopex" and normalized == "eur/tco2":
        return multiplier
    raise ValueError(f"Unexpected DEA CCS unit '{unit_src}' for variable '{variable}'")


def _extract_embedded_year(label: str) -> int:
    """Extract a trailing 4-digit price year embedded in a DEA par label.

    A 2025 catalogue revision of the individual-heating workbook left the dedicated
    `priceyear` column blank and instead embeds the price year directly in the par label
    (e.g. `"Nominal investment (*total) [k€/unit, 2025]"`), so it has to be parsed out
    instead.
    """
    match = re.search(r"(\d{4})\D*$", label)
    if match is None:
        raise ValueError(
            f"Could not find an embedded price year in DEA label '{label}'"
        )
    return int(match.group(1))


class DEA(Dataset[pd.DataFrame]):
    """Danish Energy Agency (DEA) technology catalogue cost data.

    Covers utility-scale power/district-heating technologies, individual
    (residential) heating installations, carbon-capture technologies, and
    renewable-fuel production routes.

    Carbon-capture technologies are reported on a Euro/tCO2(/h) basis rather
    than Euro/kW; their rows carry `CO2_BASIS_UNITS` in the `unit` column
    instead of the power/heat schema, and `TechnologyCostDatabase` reads that
    unit back out of the data rather than assuming a fixed one per variable.
    DEA's oxy-fuel capture and CO2 transport/storage/liquefaction entries are
    *not* included (out of scope for a technology cost database: they price
    logistics infrastructure, not a conversion technology).

    Raw data is downloaded once from DEA's own stable media links (see `_SOURCES`) and
    cached
    locally under `self.path` as an "alldata_flat" export per source, matching the
    legacy
    script's approach (its original `ens.dk/sites/ens.dk/files/...` URLs no longer
    resolve) and
    the other agencies' checked-in-local-file convention.

    DEA revises this catalogue continuously; a handful of technologies were renamed or
    restructured by revisions made since this class was first ported (see
    `_MAIN_TECHS_LITERAL`,
    `_LABEL_SUFFIXES`, and the `pyrolysis` entries in `_RF_TECHS`/`_RF_COST_PARS` for
    specifics).
    If DEA renames or restructures a technology again, re-verify this file's mappings
    against a
    delete-and-refetch of the affected file in `self.path`.

    District heating distribution-network data are available separately via
    `get_dh_distribution_data`, in DEA's own native units (`€/km²` capacity, not `€/kW`)
    rather
    than folded into `get_costs()`'s shared schema.
    """

    name = "dea"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)
        self._dh_distribution_data = self._set_dh_distribution_data()

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Technology catalogues",
            author=["Danish Energy Agency"],
            publication="Danish Energy Agency",
            publication_year=2026,
            url="https://ens.dk/en/analyses-and-statistics/technology-catalogues",
            note=(
                "Includes data for electricity, district heating, individual heating,"
                "renewable fuels, carbon capture, and more technologies."
            ),
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        path = self.source_path / "03-technology" / "cost" / "dea"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _set_data(self) -> pd.DataFrame:
        cache_path = self.path / "dea_processed.feather"
        if cache_path.exists() and not get_active_cache_settings().overwrite_dea:
            return pd.read_feather(cache_path).set_index(INDEX_NAMES)

        financial, technical = self._load("main", extra_technical_cats=("Technology-specific data",))
        ih_financial, ih_technical = self._load("ih")
        ccs_financial, ccs_technical = self._load("ccs")
        rf_financial, rf_technical = self._load("rf", rf_category_fixup=True)

        rows: list[tuple] = []
        rows += self._parse_main(financial, technical)
        rows += self._parse_individual_heating(ih_financial, ih_technical)
        rows += self._parse_ccs(ccs_financial, ccs_technical)
        rows += self._parse_renewable_fuels(rf_financial, rf_technical)

        data = pd.DataFrame(rows, columns=INDEX_NAMES + VALUE_COLUMNS)
        data = data.drop_duplicates(subset=INDEX_NAMES)
        data = data.set_index(INDEX_NAMES).sort_index()
        data.reset_index().to_feather(cache_path)
        return data

    def _load(
        self,
        source: str,
        rf_category_fixup: bool = False,
        extra_technical_cats: tuple[str, ...] = (),
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Load one of DEA's "alldata_flat" workbooks and split it into
        financial/technical.

        Downloads the workbook to `self.path` on first use (see `_download`); subsequent
        loads
        read the cached local file. Mirrors the legacy script's `load_DEA`: split rows
        by the
        `cat` column into "Financial data" and "Energy/technical data". The
        renewable-fuels
        workbook's `cat` column has several whitespace-inconsistent "Financial data..."
        variants
        (`rf_category_fixup=True` normalizes them to "Financial data", exactly as the
        legacy
        script did); every other source uses `cat` values that already match exactly.
        `extra_technical_cats` adds further `cat` values to the technical rows; the
        electricity & district heating workbook reports the heat efficiency of
        back-pressure CHP plants under "Technology-specific data".
        """
        filename, url = _SOURCES[source]
        file_path = self.path / filename
        if get_active_cache_settings().overwrite_dea or not file_path.exists():
            self._download(url, file_path)
        raw = self._read_source_workbook(file_path)
        if rf_category_fixup:
            raw = raw.copy()
            contains_financial_data = raw["cat"].str.contains(
                "Financial data", na=False
            )
            raw.loc[contains_financial_data, "cat"] = "Financial data"
        financial = self._clean(raw[raw["cat"] == "Financial data"])
        technical = self._clean(raw[raw["cat"].isin(("Energy/technical data", *extra_technical_cats))]
        )
        return financial, technical

    @staticmethod
    def _read_source_workbook(file_path: Path) -> pd.DataFrame:
        """Read either of the workbook layouts currently published by DEA.

        DEA is gradually replacing the original ``alldata_flat`` worksheets with
        ``alldata_long`` worksheets. The newer worksheet has an introductory row and
        uses a lowercase name for the technology column. This method presents both
        layouts to the existing parser in the same form.

        Args:
            file_path: Downloaded DEA Excel workbook.

        Returns:
            Source rows with consistent column names.

        Raises:
            ValueError: If the workbook has neither supported worksheet or lacks
                columns required by the parser.
        """
        with pd.ExcelFile(file_path) as workbook:
            if "alldata_long" in workbook.sheet_names:
                raw = pd.read_excel(workbook, sheet_name="alldata_long", header=1)
            elif "alldata_flat" in workbook.sheet_names:
                raw = pd.read_excel(workbook, sheet_name="alldata_flat")
            else:
                available = ", ".join(map(str, workbook.sheet_names))
                raise ValueError(
                    f"DEA workbook '{file_path.name}' contains neither "
                    f"'alldata_long' nor 'alldata_flat'. Available worksheets: "
                    f"{available}"
                )

        raw = raw.rename(columns={"technology": "Technology"})
        missing_columns = sorted(_REQUIRED_SOURCE_COLUMNS.difference(raw.columns))
        if missing_columns:
            raise ValueError(
                f"DEA workbook '{file_path.name}' is missing required columns: "
                f"{', '.join(missing_columns)}"
            )
        return raw

    @staticmethod
    def _download(url: str, dest: Path) -> None:
        """Fetch a DEA source workbook and cache it locally."""
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request) as response:
            dest.write_bytes(response.read())

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        """Strip whitespace from string cells and drop rows whose `val` is a non-numeric
        placeholder (e.g. "-" for "not applicable"), matching the legacy script's own
        pre-processing step."""
        df = df.copy()
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        df["val"] = pd.to_numeric(df["val"], errors="coerce")
        return df.dropna(subset=["val"])

    def _parse_main(
        self, financial: pd.DataFrame, technical: pd.DataFrame
    ) -> list[tuple]:
        rows: list[tuple] = []
        for technology, (
            dea_tech,
            category,
            dea_input,
            fixed_size,
        ) in _MAIN_TECHS.items():
            for plant_size in ("S", "M", "L"):
                size = _dea_size(plant_size, technology)
                if fixed_size is not None and size != fixed_size:
                    continue
                label = " - ".join(
                    [dea_tech, category, dea_input, size]
                ) + _LABEL_SUFFIXES.get(technology, "")
                output_size = "M" if technology in _PV_TECHS else plant_size
                rows += self._parse_main_label(
                    financial, technical, label, technology, output_size
                )
        for technology, (label, plant_size) in _MAIN_TECHS_LITERAL.items():
            rows += self._parse_main_label(
                financial, technical, label, technology, plant_size
            )
        return rows

    def _parse_main_label(
        self,
        financial: pd.DataFrame,
        technical: pd.DataFrame,
        label: str,
        technology: str,
        plant_size: str,
    ) -> list[tuple]:
        tech_rows = financial[financial["Technology"] == label]
        if tech_rows.empty:
            return []
        rows: list[tuple] = []
        for scenario, est in _SCENARIOS.items():
            for variable, var_label in _COST_VAR_LABELS.items():
                par = self._find_cost_par(tech_rows, var_label)
                if par is None:
                    continue
                sel = tech_rows[(tech_rows["par"] == par) & (tech_rows["est"] == est)]
                if sel.empty:
                    continue
                unit_src = sel["unit"].iloc[0]
                multiplier = _convert_main_unit(unit_src, variable)
                schema_unit = {
                    "capex": "Euro/kW",
                    "fopex": "Euro/kW",
                    "vopex": "Euro/MWh",
                }[variable]
                for _, row in sel.iterrows():
                    rows.append(
                        (
                            technology,
                            plant_size,
                            scenario,
                            variable,
                            int(row["year"]),
                            float(row["val"]) * multiplier,
                            schema_unit,
                            int(row["priceyear"]),
                            float(row["val"]),
                            unit_src,
                        )
                    )
        rows += self._parse_main_tech_vars(technical, label, technology, plant_size)
        return rows

    @staticmethod
    def _find_cost_par(tech_rows: pd.DataFrame, var_label: str) -> str | None:
        """DEA reports electric- and heat-basis figures under different par
        strings; prefer the electric one, fall back to heat. O&M labels use
        "EUR" in current catalogues and "Euro" in older ones"""
        for suffix in (
            ("MW_e", "MW_h") if var_label != "Variable O&M" else ("MWh_e", "MWh_h")
        ):
            year_str = "/y" if var_label == "Fixed O&M" else ""
            moneys = ("MEUR",) if var_label == "Nominal investment" else ("Euro", "EUR")
            for money in moneys:
                par = f"{var_label} (*total) [{money}/{suffix}{year_str}]"
                if (tech_rows["par"] == par).any():
                    return par
        return None

    @staticmethod
    def _parse_main_tech_vars(
        technical: pd.DataFrame, label: str, technology: str, plant_size: str
    ) -> list[tuple]:
        tech_rows = technical[technical["Technology"] == label]
        if tech_rows.empty:
            return []
        rows: list[tuple] = []
        tech_pars = {
            "efficiency": [
                "Electrical efficiency (net, name plate) []",
                "Heat efficiency (net, name plate) []",
            ],
            "heat_efficiency": ["Heat efficiency (net, name plate) []"],
            "lifetime": ["Technical lifetime [years]"],
            "construction_time": ["Construction time [years]"],
        }
        schema_units = {"efficiency": "1", "heat_efficiency": "1", "lifetime": "1", "construction_time": "1"}
        source_units = {
            "efficiency": "-",
            "heat_efficiency": "-",
            "lifetime": "years",
            "construction_time": "years",
        }
        for variable, candidate_pars in tech_pars.items():
            for par in candidate_pars:
                sel = tech_rows[tech_rows["par"] == par]
                if sel.empty:
                    continue
                for scenario, est in _SCENARIOS.items():
                    scen_sel = sel[sel["est"] == est]
                    for _, row in scen_sel.iterrows():
                        rows.append(
                            (
                                technology,
                                plant_size,
                                scenario,
                                variable,
                                int(row["year"]),
                                float(row["val"]),
                                schema_units[variable],
                                None,
                                float(row["val"]),
                                source_units[variable],
                            )
                        )
                break
        return rows

    def _parse_individual_heating(
        self, financial: pd.DataFrame, technical: pd.DataFrame
    ) -> list[tuple]:
        rows: list[tuple] = []
        for technology, (dea_tech, buildage) in _IH_TECHS.items():
            for plant_size, size in _IH_SIZE_MAP.items():
                label = f"{dea_tech} - {size} - {buildage}"
                fin_rows = financial[financial["Technology"] == label]
                tech_rows = technical[technical["Technology"] == label]
                if fin_rows.empty:
                    continue
                capacity_kw = self._ih_capacity_kw(tech_rows)
                if capacity_kw is None:
                    continue
                for scenario, est in _SCENARIOS.items():
                    rows += self._parse_ih_costs(
                        fin_rows, technology, plant_size, scenario, est, capacity_kw
                    )
                rows += self._parse_ih_tech_vars(tech_rows, technology, plant_size)
        return rows

    @staticmethod
    def _ih_capacity_kw(tech_rows: pd.DataFrame) -> float | None:
        """Per-unit heat production capacity [kW], needed to convert DEA's
        per-appliance ("/unit") capex and fopex figures to a per-kW basis."""
        sel = tech_rows[
            (tech_rows["par"] == "Heat production capacity for one unit [kW_h]")
            & (tech_rows["est"] == "ctrl")
        ]
        if sel.empty:
            return None
        return float(sel["val"].iloc[0])

    @staticmethod
    def _parse_ih_costs(
        fin_rows: pd.DataFrame,
        technology: str,
        plant_size: str,
        scenario: str,
        est: str,
        capacity_kw: float,
    ) -> list[tuple]:
        """Fills the individual-heating cost rows.

        The individual-heating workbook's `priceyear` column is blank (a 2025 catalogue
        revision); each par label embeds its price year instead (e.g. `"...[k€/unit,
        2025]"`),
        so the par is matched by its stable prefix and the year is parsed out of the
        matched
        label via `_extract_embedded_year` rather than read from `priceyear` or
        hardcoded.
        """
        rows: list[tuple] = []
        par_prefix_by_var = {
            "capex": "Nominal investment (*total) [k€/unit,",
            "fopex": "Fixed O&M (*total) [€/unit/y,",
            "vopex": "Variable O&M (*total) [€/kWh,",
        }
        for variable, prefix in par_prefix_by_var.items():
            matching_pars = [
                par
                for par in fin_rows["par"].unique()
                if isinstance(par, str) and par.startswith(prefix)
            ]
            if not matching_pars:
                continue
            par = matching_pars[0]
            money_year_src = _extract_embedded_year(par)
            sel = fin_rows[(fin_rows["par"] == par) & (fin_rows["est"] == est)]
            if sel.empty:
                continue
            for _, row in sel.iterrows():
                value_src = float(row["val"])
                if variable == "capex":
                    value = value_src * 1000 / capacity_kw  # k Euro/unit -> Euro/kW
                    unit = "Euro/kW"
                elif variable == "fopex":
                    value = value_src / capacity_kw  # Euro/unit/y -> Euro/kW
                    unit = "Euro/kW"
                else:
                    value = value_src * 1000  # Euro/kWh -> Euro/MWh
                    unit = "Euro/MWh"
                rows.append(
                    (
                        technology,
                        plant_size,
                        scenario,
                        variable,
                        int(row["year"]),
                        value,
                        unit,
                        money_year_src,
                        value_src,
                        par,
                    )
                )
        return rows

    @staticmethod
    def _parse_ih_tech_vars(
        tech_rows: pd.DataFrame, technology: str, plant_size: str
    ) -> list[tuple]:
        rows: list[tuple] = []
        tech_pars = {
            "efficiency": "Heat efficiency (annual average, net) [p.u.]",
            "lifetime": "Technical economic lifetime [years]",
        }
        schema_units = {"efficiency": "-", "lifetime": "1"}
        source_units = {"efficiency": "-", "lifetime": "years"}
        for variable, par in tech_pars.items():
            sel = tech_rows[(tech_rows["par"] == par) & (tech_rows["est"] == "ctrl")]
            for _, row in sel.iterrows():
                for scenario in _SCENARIOS:
                    rows.append(
                        (
                            technology,
                            plant_size,
                            scenario,
                            variable,
                            int(row["year"]),
                            float(row["val"]),
                            schema_units[variable],
                            None,
                            float(row["val"]),
                            source_units[variable],
                        )
                    )
        return rows

    def _parse_ccs(
        self, financial: pd.DataFrame, technical: pd.DataFrame
    ) -> list[tuple]:
        rows: list[tuple] = []
        for technology, dea_label in _CCS_TECHS.items():
            cost_pars = _CCS_COST_PARS.get(technology, _CCS_COST_PARS["_default"])
            fin_rows = financial[financial["Technology"] == dea_label]
            tech_rows = technical[technical["Technology"] == dea_label]
            if fin_rows.empty:
                continue
            for scenario, est in _CCS_SCENARIOS.items():
                for variable, par in cost_pars.items():
                    sel = fin_rows[(fin_rows["par"] == par) & (fin_rows["est"] == est)]
                    if sel.empty:
                        continue
                    unit_src = sel["unit"].iloc[0]
                    multiplier = _convert_ccs_unit(unit_src, variable)
                    for _, row in sel.iterrows():
                        rows.append(
                            (
                                technology,
                                "M",
                                scenario,
                                variable,
                                int(row["year"]),
                                float(row["val"]) * multiplier,
                                CO2_BASIS_UNITS[variable],
                                int(row["priceyear"]),
                                float(row["val"]),
                                unit_src,
                            )
                        )
            rows += self._parse_lifetime_and_construction_time(
                tech_rows, technology, "M", _CCS_SCENARIOS
            )
        return rows

    def _parse_renewable_fuels(
        self, financial: pd.DataFrame, technical: pd.DataFrame
    ) -> list[tuple]:
        """Fills the renewable-fuels cost rows.

        The renewable-fuels workbook's `priceyear` column is entirely blank;
        `_RF_MONEY_YEAR_SRC`
        supplies the price year instead, taken from the workbook's own Index sheet
        statement of
        its price basis (see that constant's definition).
        """
        rows: list[tuple] = []
        for technology, dea_label in _RF_TECHS.items():
            scenarios = _RF_SCENARIOS_DEFAULT
            money_year_src = _RF_MONEY_YEAR_SRC.get(
                technology, _RF_DEFAULT_MONEY_YEAR_SRC
            )
            fin_rows = financial[financial["Technology"] == dea_label]
            tech_rows = technical[technical["Technology"] == dea_label]
            if fin_rows.empty:
                continue
            schema_units = {"capex": "Euro/kW", "fopex": "Euro/kW", "vopex": "Euro/MWh"}
            for scenario, est in scenarios.items():
                for variable, (par, multiplier) in _RF_COST_PARS[technology].items():
                    sel = fin_rows[(fin_rows["par"] == par) & (fin_rows["est"] == est)]
                    if sel.empty:
                        continue
                    share_pars = _RF_COST_SHARES.get((technology, variable))
                    relative = (
                        technology in _RF_RELATIVE_BOUNDS_TECHS and est != scenarios["ref"]
                    )
                    for _, row in sel.iterrows():
                        year = int(row["year"])
                        share = (
                            1.0
                            if share_pars is None
                            else self._rf_cost_share(fin_rows, share_pars, est, year)
                        )
                        value = float(row["val"])
                        if relative:
                            value *= self._rf_reference_value(
                                fin_rows, par, scenarios["ref"], year
                            )
                        rows.append(
                            (
                                technology,
                                "M",
                                scenario,
                                variable,
                                year,
                                value * multiplier * share,
                                schema_units[variable],
                                money_year_src,
                                float(row["val"]),
                                par,
                            )
                        )
            rows += self._parse_lifetime_and_construction_time(
                tech_rows, technology, "M", scenarios
            )
        return rows

    @staticmethod
    def _parse_lifetime_and_construction_time(
        tech_rows: pd.DataFrame,
        technology: str,
        plant_size: str,
        scenarios: dict[str, str],
    ) -> list[tuple]:
        rows: list[tuple] = []
        tech_pars = {
            "lifetime": "Technical lifetime [years]",
            "construction_time": "Construction time [years]",
        }
        for variable, par in tech_pars.items():
            sel = tech_rows[tech_rows["par"] == par]
            if sel.empty:
                continue
            for scenario, est in scenarios.items():
                scen_sel = sel[sel["est"] == est]
                for _, row in scen_sel.iterrows():
                    rows.append(
                        (
                            technology,
                            plant_size,
                            scenario,
                            variable,
                            int(row["year"]),
                            float(row["val"]),
                            "1",
                            None,
                            float(row["val"]),
                            "years",
                        )
                    )
        return rows
    
    @staticmethod
    def _rf_cost_share(
        fin_rows: pd.DataFrame, share_pars: tuple[str, str], est: str, year: int
    ) -> float:
        """Share of a reported renewable-fuel cost for one estimate and year
        (see `_RF_COST_SHARES`)."""
        values: dict[str, float] = {}
        for par in share_pars:
            sel = fin_rows[
                (fin_rows["par"] == par)
                & (fin_rows["est"] == est)
                & (fin_rows["year"] == year)
            ]
            if sel.empty:
                raise ValueError(
                    f"DEA row '{par}' ({est}, {year}) needed to split a renewable-fuel "
                    "cost is missing."
                )
            values[par] = float(sel["val"].iloc[0])
        part_par, total_par = share_pars
        return values[part_par] / values[total_par]

    @staticmethod
    def _rf_reference_value(
        fin_rows: pd.DataFrame, par: str, ref_est: str, year: int
    ) -> float:
        """Central estimate of a renewable-fuel cost in `year`, interpolated
        between reported years (see `_RF_RELATIVE_BOUNDS_TECHS`)."""
        ref = fin_rows[(fin_rows["par"] == par) & (fin_rows["est"] == ref_est)]
        if ref.empty:
            raise ValueError(
                f"DEA row '{par}' ({ref_est}) needed to scale relative cost bounds "
                "is missing."
            )
        ref = ref.groupby("year")["val"].first().sort_index()
        return float(np.interp(year, ref.index.astype(float), ref.to_numpy(float)))
    
    def _set_dh_distribution_data(self) -> pd.DataFrame:
        financial, technical = self._load("dh_transport")
        rows: list[tuple] = []
        for area_type, ws in _DH_DISTRIBUTION_SHEETS.items():
            rows += self._parse_dh_distribution_sheet(
                financial, technical, ws, area_type
            )
        data = pd.DataFrame(
            rows, columns=_DH_DISTRIBUTION_INDEX_NAMES + _DH_DISTRIBUTION_VALUE_COLUMNS
        )
        data = data.drop_duplicates(subset=_DH_DISTRIBUTION_INDEX_NAMES)
        return data.set_index(_DH_DISTRIBUTION_INDEX_NAMES).sort_index()

    @staticmethod
    def _parse_dh_distribution_sheet(
        financial: pd.DataFrame, technical: pd.DataFrame, ws: str, area_type: str
    ) -> list[tuple]:
        fin_rows = financial[financial["ws"] == ws]
        tech_rows = technical[technical["ws"] == ws]
        rows: list[tuple] = []
        for variable, par in _DH_DISTRIBUTION_COST_PARS.items():
            sel_all = fin_rows[fin_rows["par"] == par]
            for scenario, est in _CCS_SCENARIOS.items():
                sel = sel_all[sel_all["est"] == est]
                for _, row in sel.iterrows():
                    rows.append(
                        (
                            area_type,
                            variable,
                            scenario,
                            int(row["year"]),
                            float(row["val"]),
                            row["unit"],
                            _DH_MONEY_YEAR_SRC,
                            float(row["val"]),
                            row["unit"],
                        )
                    )
        for variable, par in _DH_DISTRIBUTION_TECH_PARS.items():
            sel_all = tech_rows[tech_rows["par"] == par]
            for scenario, est in _CCS_SCENARIOS.items():
                sel = sel_all[sel_all["est"] == est]
                for _, row in sel.iterrows():
                    rows.append(
                        (
                            area_type,
                            variable,
                            scenario,
                            int(row["year"]),
                            float(row["val"]),
                            row["unit"],
                            None,
                            float(row["val"]),
                            row["unit"],
                        )
                    )
        return rows

    # -------- methods ------------------------

    def get_costs(self) -> pd.DataFrame:
        """Return the parsed, standardized DEA cost/tech data (see `_cost_schema`)."""
        return self.data.copy()

    def get_dh_distribution_data(self) -> pd.DataFrame:
        """Return district heating distribution-network cost/tech data, in DEA's native
        units.

        Index: `area_type` (`"suburban"`/`"city"`/`"new_area"`, DEA's three
            network-density
        variants), `variable`
        (`"capex"`/`"fopex"`/`"vopex"`/`"lifetime"`/`"construction_time"`),
        `scenario` (`"min"`/`"ref"`/`"max"`), `year`. Columns match `get_costs()`
        (`value`/`unit`/`money_year_src`/`value_src`/`unit_src`), except `capex`'s
        `unit` is
        `M€/km²` (network cost per unit of service area) rather than a `€/kW` figure --
        this
        table is intentionally kept separate from `get_costs()`/`_cost_schema`'s shared
        Euro/kW(h) schema rather than forcing an area-based figure into it. `fopex`
        (`€/MW/year`) and `vopex` (`€/MWh`) are on a normal capacity/energy basis and
        would fit
        the shared schema, but are kept alongside `capex` here for a single consistent
        table.

        DEA also reports district heating *transmission* (bulk, inter-node pipelines,
        distinct
        from this last-mile distribution-network data) in the same source workbook; that
        data is
        not extracted here (see `_DH_DISTRIBUTION_SHEETS`).
        """
        return self._dh_distribution_data.copy()

    def get_conversion_factor_electrolysis(self):
        """returns the conversion factor for electrolysis.

        Hydrogen production via PEMEC electrolysis for 100 MW plant,
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        return [{"electricity": {"default_value": 1 / 0.526, "unit": "GW/GW"}}]

    def get_conversion_factor_anaerobic_digestion(self):
        """returns the conversion factor for anaerobic digestion.

        Values from the DEA technology catalogue for renewable fuels (Biogas
        plant, Basic plant, large [~6,000 Nm3 CH4/h]), share of output energy, 2020). 
        The biogas yield of 55% of the feedstock energy is an assumption; the 
        remaining feedstock energy is assumed to leave the plant with the digestate.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        biogas_yield = 0.55
        return [
            {"biogas_feedstock": {"default_value": 1 / biogas_yield, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.0211, "unit": "GWh/GWh"}},
            {"heat": {"default_value": 0.0505, "unit": "GWh/GWh"}},
            {"digestate": {"default_value": (1 - biogas_yield)/biogas_yield, "unit": "GWh/GWh"}},
        ]

    def get_conversion_factor_biogas_upgrading(self):
        """returns the conversion factor for biogas upgrading.

        Values from the DEA technology catalogue for renewable fuels (Biogas
        upgrading - Amine scrubber [~6,000 Nm3 CH4/h]).
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        return [
            {"biogas": {"default_value": 1 / 0.9905, "unit": "GWh/GWh"}},
            {"heat": {"default_value": 0.1032 / 0.9905, "unit": "GWh/GWh"}},
        ]

    def get_conversion_factor_gasification(self):
        """returns the conversion factor for gasification.

        Values from the DEA technology catalogue for renewable fuels
        (Gasifier, biomass, bio-SNG, medium - large scale), assuming a bio-SNG
        conversion efficiency of 60% and heat co-generation of 20% (2020 values).
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        efficiency = 0.6
        return [
            {"gasif_biomass": {"default_value": 1 / efficiency, "unit": "GWh/GWh"}},
            {"district_heat": {"default_value": 0.2 / efficiency, "unit": "GWh/GWh"}},
        ]

    def get_conversion_factor_biogas_methanation(self):
        """returns the conversion factor for biogas methanation.

        Values from the DEA technology catalogue for renewable fuels (92
        Methanation of Biogas, "SNG from Biogas"): per MWh of total input,
        0.53 MWh biogas, 0.46 MWh hydrogen and 0.01 MWh electricity yield
        0.89 MWh SNG and 0.10 MWh district heat. The CO2 in the biogas is
        methanised with the hydrogen. Normalized to the SNG (natural gas)
        reference carrier.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        sng_output = 0.89  # MWh SNG / MWh total input
        return [
            {"biogas": {"default_value": 0.53 / sng_output, "unit": "GWh/GWh"}},
            {"hydrogen": {"default_value": 0.46 / sng_output, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.01 / sng_output, "unit": "GWh/GWh"}},
            {"district_heat": {"default_value": 0.10 / sng_output, "unit": "GWh/GWh"}},
        ]
    
    def get_conversion_factor_fischer_tropsch(self):
        """returns the conversion factor for fischer-tropsch.

        Values from the DEA technology catalogue for renewable fuels
        (Hydrogen to Jet Fuel), normalized to the oil reference carrier,
        assuming all output is kerosene-equivalent oil.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        oil_per_input = 0.65  # MWh oil / MWh input
        # DEA tonFTtoGWh = 44 GWh / 3.6 (GJ->GWh not applicable, ton basis) / 1000
        ton_ft_to_gwh = 44 / (Constants.GJ_PER_MWH * 1000)  # GWh/ton
        return [
            {"hydrogen": {"default_value": 0.995 / oil_per_input, "unit": "GWh/GWh"}},
            {
                "carbon": {
                    "default_value": (4.3 / ton_ft_to_gwh / 1000) / oil_per_input,
                    "unit": "ktCO2/GWh",
                }
            },
            {
                "electricity": {
                    "default_value": 0.005 / oil_per_input,
                    "unit": "GWh/GWh",
                }
            },
            {
                "district_heat": {
                    "default_value": 0.25 / oil_per_input,
                    "unit": "GWh/GWh",
                }
            },
        ]

    def get_conversion_factor_pyrolysis_slow(self):
        """returns the conversion factor for slow pyrolysis.

        Values from the DEA technology catalogue for renewable fuels (87 Large
        scale slow pyrolysis (20 MW), straw feedstock), per MWh of total input:
        0.9592 MWh biomass and 0.0408 MWh electricity yield 0.4508 MWh biochar
        (modelled as hard coal), 0.1918 MWh pyrolysis oil and 0.2398 MWh heat
        from burning the pyrolysis gas on site. Normalized to the pyrolysis oil
        reference carrier.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        oil_output = 0.1918  # MWh pyrolysis oil / MWh total input (reference carrier)
        return [
            {"biomass_slow_pyrolysis": {
                "default_value": 0.9592 / oil_output, 
                "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.0408 / oil_output, "unit": "GWh/GWh"}},
            {"district_heat": {"default_value": 0.2398 / oil_output, "unit": "GWh/GWh"}},
            {"hard_coal": {"default_value": 0.4508 / oil_output, "unit": "GWh/GWh"}},
        ]

        # assumed efficiency of burning the low-calorific pyrolysis gas on site
    _PYROLYSIS_GAS_COMBUSTION_EFFICIENCY = 0.9

    def get_conversion_factor_pyrolysis_fast(self):
        """returns the conversion factor for fast pyrolysis.

        Values from the DEA technology catalogue for renewable fuels (86 Fast
        pyrolysis (25 MW), wood feedstock), per MWh of total input: 0.93 MWh
        biomass, 0.01 MWh electricity and 0.06 MWh heat yield 0.70 MWh pyrolysis
        oil and 0.15 MWh pyrolysis gas. The low-calorific pyrolysis gas is
        assumed to be burned on site (90% efficiency) to cover the heat demand;
        the remainder is supplied as district heat. Normalized to the pyrolysis
        oil reference carrier.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        oil_output = 0.70  # MWh pyrolysis oil / MWh total input
        net_heat = 0.15 * self._PYROLYSIS_GAS_COMBUSTION_EFFICIENCY - 0.06
        return [
            {
                "biomass_fast_pyrolysis": {
                    "default_value": 0.93 / oil_output,
                    "unit": "GWh/GWh",
                }
            },
            {"electricity": {"default_value": 0.01 / oil_output, "unit": "GWh/GWh"}},
            {"district_heat": {"default_value": net_heat / oil_output, "unit": "GWh/GWh"}},
        ]

    def get_cost_multiplier_pyrolysis_fast(self) -> float:
        """returns the cost multiplier for fast pyrolysis.

        DEA reports the costs per MW of output from the pyrolysis process
        (0.70 MWh oil + 0.15 MWh gas per MWh input), while the technology is
        sized by its pyrolysis oil output, so the costs are rebased by
        (oil + gas) / oil.
        """
        return (0.70 + 0.15) / 0.70

    def get_conversion_factor_haber_bosch(self):
        """returns the conversion factor for the Haber-Bosch process.

        Values from the DEA technology catalogue for renewable fuels (Green
        Ammonia plant: Hydrogen to ammonia, excl. electrolyzer and excl.
        air-separation unit).
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        return [
            {"hydrogen": {"default_value": 0.95, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.05, "unit": "GWh/GWh"}},
        ]

    def get_conversion_factor_methanol_from_hydrogen(self):
        """returns the conversion factor for methanol from hydrogen.

        Values from the DEA technology catalogue for renewable fuels
        (Methanol from hydrogen and carbon dioxide).
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        ton_meoh_to_mwh = Constants.METHANOL_KWH_PER_KG
        return [
            {"hydrogen": {"default_value": 6.4 / ton_meoh_to_mwh, "unit": "GWh/GWh"}},
            {
                "carbon": {
                    "default_value": 1.4 / ton_meoh_to_mwh,
                    "unit": "kilotCO2/GWh",
                }
            },
            {
                "electricity": {
                    "default_value": 0.1 / ton_meoh_to_mwh,
                    "unit": "GWh/GWh",
                }
            },
        ]

    def get_conversion_factor_methanol_from_biomass(self):
        """returns the conversion factor for methanol from biomass.

        Values from the DEA technology catalogue for renewable fuels (Bio
        Methanol).
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        methanol_production_biomass = 0.58
        return [
            {
                "gasif_biomass": {
                    "default_value": 1 / methanol_production_biomass,
                    "unit": "GWh/GWh",
                }
            },
            {
                "district_heat": {
                    "default_value": 0.22 / methanol_production_biomass,
                    "unit": "GWh/GWh",
                }
            },
            {
                "electricity": {
                    "default_value": 0.02 / methanol_production_biomass,
                    "unit": "GWh/GWh",
                }
            },
        ]

    def get_conversion_factor_methanol_from_biogas(self):
        """returns the conversion factor for methanol from biogas.

        Values from the DEA technology catalogue for renewable fuels (97
        Methanol from biogas and hydrogen), per ton of methanol: 4.0959 MWh
        biogas, 2.48 MWh hydrogen, 0.34 MWh electricity and 0.153 MWh net
        steam, which is modelled as heat. Oxygen and water inputs and the
        effluent gas output are not modelled; methanol (19.9 GJ/ton) is the
        only output. Normalized to the methanol reference carrier.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        methanol_mwh_per_ton = 19.9 / Constants.GJ_PER_MWH  # DEA LHV, 19.9 GJ/ton
        return [
            {
                "biogas": {
                    "default_value": 4.0959 / methanol_mwh_per_ton,
                    "unit": "GWh/GWh",
                }
            },
            {
                "hydrogen": {
                    "default_value": 2.48 / methanol_mwh_per_ton,
                    "unit": "GWh/GWh",
                }
            },
            {
                "electricity": {
                    "default_value": 0.34 / methanol_mwh_per_ton,
                    "unit": "GWh/GWh",
                }
            },
            {
                "heat": {
                    "default_value": 0.153 / methanol_mwh_per_ton,
                    "unit": "GWh/GWh",
                }
            },
        ]

# TODO: add glycerine as a co-product to the FAME conversion factor, once it is modelled in the energy system.
    def get_conversion_factor_FAME(self):
        """returns the conversion factor for FAME biodiesel production.

        Values from the DEA technology catalogue for renewable fuels (101 FAME
        biodiesel (veg. oil), "Vegetable Oil FAME", 2020 values), per MWh of
        total input: 0.926 MWh vegetable oil, 0.046 MWh methanol, 0.024 MWh
        natural gas and 0.004 MWh electricity yield 0.903 MWh biodiesel and
        0.039 MWh glycerine. The biodiesel is modelled as diesel and the
        glycerine is not (yet) modelled. Normalized to the diesel reference carrier.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        biodiesel_output = 0.903  # MWh biodiesel / MWh total input
        return [
            {
                "oily_biomass": {
                    "default_value": 0.926 / biodiesel_output,
                    "unit": "GWh/GWh",
                }
            },
            {
                "methanol": {
                    "default_value": 0.046 / biodiesel_output,
                    "unit": "GWh/GWh",
                }
            },
            {
                "natural_gas": {
                    "default_value": 0.024 / biodiesel_output,
                    "unit": "GWh/GWh",
                }
            },
            {
                "electricity": {
                    "default_value": 0.004 / biodiesel_output,
                    "unit": "GWh/GWh",
                }
            },
        ]

    def get_conversion_factor_HVO_jet(self):
        """returns the conversion factor for HVO jet fuel.

        Values from the DEA technology catalogue for renewable fuels (103 HVO jet
        fuel), per MWh of total input: 0.779 MWh vegetable oil, 0.099 MWh
        hydrogen, 0.119 MWh natural gas and 0.003 MWh electricity yield 0.66 MWh
        jet fuel (modelled as kerosene) and 0.0651 MWh naphtha. The LPG, fuel gas
        and district heat co-products are not modelled. Normalized to the
        kerosene reference carrier.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        jet_output = 0.66  # MWh jet fuel / MWh total input
        return [
            {"oily_biomass": {"default_value": 0.779 / jet_output, "unit": "GWh/GWh"}},
            {"hydrogen": {"default_value": 0.099 / jet_output, "unit": "GWh/GWh"}},
            {"natural_gas": {"default_value": 0.119 / jet_output, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.003 / jet_output, "unit": "GWh/GWh"}},
            {"naphtha": {"default_value": 0.0651 / jet_output, "unit": "GWh/GWh"}},
        ]

    def get_conversion_factor_HVO_diesel(self):
        """returns the conversion factor for HVO renewable diesel.

        Values from the DEA technology catalogue for renewable fuels (104 HVO
        renewable diesel), per MWh of total input: 0.881 MWh vegetable oil,
        0.105 MWh hydrogen, 0.007 MWh natural gas and 0.008 MWh electricity yield
        0.85 MWh HVO (modelled as diesel) and 0.066 MWh naphtha. The LPG, fuel
        gas and district heat co-products are not modelled. Normalized to the
        diesel reference carrier.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        hvo_output = 0.85  # MWh HVO / MWh total input
        return [
            {"oily_biomass": {"default_value": 0.881 / hvo_output, "unit": "GWh/GWh"}},
            {"hydrogen": {"default_value": 0.105 / hvo_output, "unit": "GWh/GWh"}},
            {"natural_gas": {"default_value": 0.007 / hvo_output, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.008 / hvo_output, "unit": "GWh/GWh"}},
            {"naphtha": {"default_value": 0.066 / hvo_output, "unit": "GWh/GWh"}},
        ]
    
    def get_conversion_factor_ethanol_1G(self):
        """returns the conversion factor for first generation ethanol.

        Values from the DEA technology catalogue for renewable fuels (105 First
        generation ethanol, grain-based), per MWh of total input: 0.83 MWh
        feedstock, 0.15 MWh natural gas and 0.02 MWh electricity yield 0.46 MWh
        ethanol and 0.27 MWh distillers' dried grains (DDG, not yet modelled).
        Normalized to the ethanol reference carrier.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        ethanol_output = 0.46  # MWh ethanol / MWh total input
        return [
            {"starch_crops": {"default_value": 0.83 / ethanol_output, "unit": "GWh/GWh"}},
            {"natural_gas": {"default_value": 0.15 / ethanol_output, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 0.02 / ethanol_output, "unit": "GWh/GWh"}},
        ]

    def get_conversion_factor_ethanol_cellulosic(self):
        """returns the conversion factor for cellulosic ethanol.

        Values from the DEA technology catalogue for renewable fuels (106
        Cellulosic ethanol), per MWh of feedstock: 0.29 (2020) / 0.37 (2030) MWh
        ethanol and 0.04 / 0.05 MWh electricity; the lignin residue covers the
        process heat. The values are interpolated to 2026, since the efficiency
        improves strongly until 2030. Normalized to the ethanol reference carrier.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        ethanol_output = 0.29 + (0.37 - 0.29) * 0.6  # 2026, MWh/MWh feedstock
        electricity_output = 0.04 + (0.05 - 0.04) * 0.6  # 2026
        return [
            {
                "cellulosic_biomass": {
                    "default_value": 1 / ethanol_output,
                    "unit": "GWh/GWh",
                }
            },
            {
                "electricity": {
                    "default_value": electricity_output / ethanol_output,
                    "unit": "GWh/GWh",
                }
            },
        ]

    def get_co2_from_ethanol_fermentation(self) -> float:
        """returns the CO2 released by fermentation per unit of ethanol
        [tCO2/MWh ethanol].

        From the fermentation stoichiometry (C6H12O6 -> 2 C2H5OH + 2 CO2, and the
        same CO2-to-ethanol ratio for C5 sugars): 88/92 = 0.957 tCO2 per ton of
        ethanol, with the DEA ethanol heating value of 26.9 GJ/ton. This is the
        theoretical value, an upper bound for the recoverable CO2.
        """
        co2_per_ton_ethanol = 2 * 44.01 / (2 * 46.07)
        ethanol_mwh_per_ton = 26.9 / Constants.GJ_PER_MWH
        return co2_per_ton_ethanol / ethanol_mwh_per_ton
    
    def get_conversion_factor_DAC(self):
        """returns the conversion factor for DAC.

        Values from the DEA technology catalogue for carbon capture,
        transport and storage (Solid Adsorption Direct Air Capture Plant,
        p. 81).
        https://ens.dk/en/analyses-and-statistics/technology-data-carbon-capture-transport-and-storage
        """
        return [
            {"electricity": {"default_value": 0.8, "unit": "GWh/kilotCO2"}},
            {
                "heat": {
                    "default_value": 9.5 / Constants.GJ_PER_MWH,
                    "unit": "GWh/kilotCO2",
                }
            },
        ]

    def get_conversion_factor_SMR_CCS(self):
        """returns the conversion factor for SMR CCS.

        Values from the DEA technology catalogue for carbon capture,
        transport and storage (Post-combustion carbon capture retrofit -
        100 MW(th) WtE or biomass CHP plant, used as a proxy entry),
        assuming all heat demand for the capture process is supplied from
        natural gas.
        https://ens.dk/en/analyses-and-statistics/technology-data-carbon-capture-transport-and-storage
        """
        return [
            {"natural_gas": {"default_value": 0.833, "unit": "GWh/kilotCO2"}},
            {"electricity": {"default_value": 0.03, "unit": "GWh/kilotCO2"}},
        ]

    def get_conversion_factor_biogas_upgrading_CCS(self):
        """returns the conversion factor for biogas upgrading CCS.

        Electricity demand for drying, compressing and liquefying the CO2
        off-gas of biogas upgrading, from the DEA technology catalogue for
        carbon capture, transport and storage (Liquefaction for biogas plant
        retrofit, 2025): 68 kWh/tCO2 compression, 2 kWh/tCO2 drying and
        63 kWh/tCO2 liquefaction. The CO2 is already separated by the
        upgrading, so no capture heat is needed.
        https://ens.dk/en/analyses-and-statistics/technology-data-carbon-capture-transport-and-storage
        """
        electricity = (68 + 2 + 63) / 1000  # kWh/tCO2 -> GWh/kilotCO2
        return [{"electricity": {"default_value": electricity, "unit": "GWh/kilotCO2"}}]

    def get_co2_content_biogas(self) -> float:
        """returns the CO2 contained in raw biogas [tCO2/MWh biogas].

        From the DEA technology catalogue for renewable fuels (Biogas plant,
        Basic plant, large): 86,477 tCO2/year alongside 52.123 mill. Nm3
        CH4/year, with a methane lower heating value of 35.8 MJ/Nm3.
        https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        """
        co2_ton_per_year = 86_477
        ch4_mwh_per_year = 52.123e6 * 35.8 / (Constants.GJ_PER_MWH * 1000)
        return co2_ton_per_year / ch4_mwh_per_year

    def get_conversion_factor_district_heating_grid(self):
        """returns the conversion factor for district heating grids.

        Based on DEA district-heating distribution-network energy losses
        (reference scenario, suburban network).
        """
        data = self.get_dh_distribution_data()
        cf = 1 - data.loc[("suburban", "energy_losses", "ref"), "value"].iloc[0] / 100
        return [{"district_heat": {"default_value": 1 / cf, "unit": "GW/GW"}}]

    def get_conversion_factor_cement_post_comb(self):
        """returns the conversion factor for cement post-combustion capture.

        Values from the DEA technology catalogue for carbon capture,
        transport and storage (Post-combustion carbon capture in a cement
        plant), assuming the fuel-for-cement input is directly converted
        into heat for the capture process.
        https://ens.dk/en/analyses-and-statistics/technology-data-carbon-capture-transport-and-storage
        """
        return [
            {"electricity": {"default_value": 0.025, "unit": "GWh/kilotCO2"}},
            {"fuel_for_cement": {"default_value": 0.833, "unit": "GWh/kilotCO2"}},
            {"district_heat": {"default_value": 1.65, "unit": "GWh/kilotCO2"}},
        ]

    def get_capture_rate_CCS(self):
        """returns the capture rate for cement post-combustion capture.

        Values from the DEA technology catalogue for carbon capture,
        transport and storage (Post-combustion carbon capture in a cement
        plant).
        https://ens.dk/en/analyses-and-statistics/technology-data-carbon-capture-transport-and-storage
        """
        return 0.9
