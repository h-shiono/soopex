"""Pydantic data models for SOOPEX header sections and the SoopObs container."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, model_validator

DataSource = Literal["receiver", "simulation"]
ObservationType = Literal["dd", "raw_doppler", "raw_freq"]
DopplerUnit = Literal["m/s", "Hz"]
FrequencyUnit = Literal["Hz"]
TimeSystem = Literal["GPST", "UTC", "TAI"]
TimeFormat = Literal["gps_seconds", "iso8601", "unix"]
OrbitSourceType = Literal["TLE", "SP3", "broadcast", "operator"]

_REQUIRED_COLUMNS = ("epoch", "norad_id", "value")


class _Base(BaseModel):
    """Common Pydantic config: allow unknown fields for forward compatibility."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class FormatInfo(_Base):
    version: str
    generator: str | None = None


class Session(_Base):
    start_time: str
    end_time: str
    site_id: str
    data_source: DataSource
    duration_s: float | None = None


class ApproximatePosition(_Base):
    latitude_deg: float
    longitude_deg: float
    height_m: float
    coordinate_system: str = "WGS84"


class Site(_Base):
    approximate_position: ApproximatePosition
    name: str | None = None


class Observations(_Base):
    type: ObservationType
    time_system: TimeSystem
    time_format: TimeFormat
    columns: list[str]
    doppler_unit: DopplerUnit | None = None
    frequency_unit: FrequencyUnit | None = None
    diff_interval_s: float | None = None
    reference_frequency_hz: float | None = None

    @model_validator(mode="after")
    def _check_conditional(self) -> Observations:
        if self.type == "dd" and self.diff_interval_s is None:
            raise ValueError("observations.diff_interval_s is required when type='dd'")
        if self.type in ("dd", "raw_doppler") and self.doppler_unit is None:
            raise ValueError(
                "observations.doppler_unit is required when type is 'dd' or 'raw_doppler'"
            )
        if self.type == "raw_freq" and self.frequency_unit is None:
            raise ValueError("observations.frequency_unit is required when type='raw_freq'")
        missing = [c for c in _REQUIRED_COLUMNS if c not in self.columns]
        if missing:
            raise ValueError(f"observations.columns missing required entries: {missing}")
        return self


class OrbitSource(_Base):
    type: OrbitSourceType
    source: str
    propagator: str | None = None
    tle_file: str | None = None
    sp3_file: str | None = None
    epoch_age_max_h: float | None = None

    @model_validator(mode="after")
    def _check_conditional(self) -> OrbitSource:
        if self.type == "TLE" and not self.propagator:
            raise ValueError("orbit_source.propagator is required when type='TLE'")
        return self


class AntennaPointing(_Base):
    mode: str | None = None
    azimuth_deg: float | None = None
    elevation_deg: float | None = None


class LNB(_Base):
    type: str | None = None
    lo_frequency_hz: float | None = None
    lo_stability: str | None = None
    lo_stability_ppm: float | None = None


class Antenna(_Base):
    type: str | None = None
    dish_diameter_m: float | None = None
    gain_dBi: float | None = None  # noqa: N815 — spec field name uses dBi casing
    pointing: AntennaPointing | None = None
    lnb: LNB | None = None


class SDR(_Base):
    type: str | None = None
    serial: str | None = None
    firmware: str | None = None
    sampling_rate_hz: float | None = None
    sample_bits: int | None = None
    bandwidth_hz: float | None = None


class Receiver(_Base):
    sdr: SDR | None = None
    antenna: Antenna | None = None


class GnssReference(_Base):
    rinex_file: str | None = None
    receiver_type: str | None = None
    time_sync_method: str | None = None
    time_sync_accuracy_s: float | None = None


class AzelSource(_Base):
    method: str | None = None
    reference: str | None = None


class Processing(_Base):
    azel_source: AzelSource | None = None


class Simulation(_Base):
    software: str | None = None


class Header(_Base):
    format: FormatInfo
    session: Session
    site: Site
    observations: Observations
    orbit_source: OrbitSource
    receiver: Receiver | None = None
    gnss_reference: GnssReference | None = None
    processing: Processing | None = None
    simulation: Simulation | None = None
    comments: list[str] | None = None
    extensions: dict[str, Any] | None = None


class SoopObs:
    """Container for a SOOPEX observation set: typed header + tabular data."""

    def __init__(self, header: Header, data: pd.DataFrame) -> None:
        self.header = header
        self.data = data

    def write(self, path: str | Path, **kwargs: Any) -> None:
        """Write this observation set to a .soop (or .soop.gz) file."""
        from soopex.writer import write as _write

        _write(self, path, **kwargs)

    def select(self, **kwargs: Any) -> SoopObs:
        """Return a new SoopObs filtered by equality on the given columns."""
        df = self.data
        if df.empty or not kwargs:
            return SoopObs(header=self.header, data=df.reset_index(drop=True))
        mask = pd.Series(True, index=df.index)
        for col, val in kwargs.items():
            if col not in df.columns:
                raise KeyError(f"unknown column: {col!r}")
            mask &= df[col] == val
        return SoopObs(header=self.header, data=df[mask].reset_index(drop=True))

    def time_slice(self, start: float | str, end: float | str) -> SoopObs:
        """Return a new SoopObs with rows where start <= epoch <= end.

        For numeric time_format (gps_seconds, unix) pass floats.
        For iso8601 time_format pass ISO-8601 strings.
        """
        df = self.data
        if df.empty:
            return SoopObs(header=self.header, data=df)
        mask = (df["epoch"] >= start) & (df["epoch"] <= end)
        return SoopObs(header=self.header, data=df[mask].reset_index(drop=True))

    def to_dataframe(self) -> pd.DataFrame:
        """Return the data DataFrame with header metadata attached to .attrs."""
        df = self.data.copy()
        df.attrs["soopex_header"] = self.header.model_dump(exclude_none=True)
        return df

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SoopObs):
            return NotImplemented
        return self.header == other.header and self.data.equals(other.data)

    def __repr__(self) -> str:
        n = len(self.data)
        cols = list(self.data.columns)
        return f"SoopObs(header=Header(...), data=<{n} rows x {len(cols)} cols>)"
