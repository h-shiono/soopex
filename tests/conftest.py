"""Shared test fixtures for SOOPEX tests."""

from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


@pytest.fixture
def sample_receiver_path() -> Path:
    """Path to sample receiver .soop file."""
    return EXAMPLES_DIR / "sample_receiver.soop"


@pytest.fixture
def sample_simulation_path() -> Path:
    """Path to sample simulation .soop file."""
    return EXAMPLES_DIR / "sample_simulation.soop"


@pytest.fixture
def sample_receiver_text(sample_receiver_path: Path) -> str:
    """Raw text content of sample receiver file."""
    return sample_receiver_path.read_text(encoding="utf-8")


@pytest.fixture
def tmp_soop(tmp_path: Path) -> Path:
    """Temporary path for writing .soop files."""
    return tmp_path / "test_output.soop"


@pytest.fixture
def minimal_soop_text() -> str:
    """Minimal valid SOOPEX file content (fewest possible fields)."""
    return """\
%SOOPEX 0.1
%HEADER
format:
  version: "0.1.0"
session:
  start_time: "2026-01-01T00:00:00Z"
  end_time: "2026-01-01T00:01:00Z"
  site_id: "TEST"
  data_source: "simulation"
site:
  approximate_position:
    latitude_deg: 0.0
    longitude_deg: 0.0
    height_m: 0.0
    coordinate_system: "WGS84"
observations:
  type: "raw_doppler"
  doppler_unit: "m/s"
  time_system: "GPST"
  time_format: "gps_seconds"
  columns:
    - epoch
    - norad_id
    - value
orbit_source:
  type: "TLE"
  source: "space-track.org"
  propagator: "SGP4"
%END_HEADER
%DATA
# epoch\tnorad_id\tvalue
2247264001.000\t54321\t-0.342
2247264002.000\t54321\t-0.358
%END_DATA
"""


@pytest.fixture
def minimal_soop_file(tmp_path: Path, minimal_soop_text: str) -> Path:
    """Write minimal .soop to a temporary file and return path."""
    p = tmp_path / "minimal.soop"
    p.write_text(minimal_soop_text, encoding="utf-8")
    return p


@pytest.fixture
def empty_data_soop_text() -> str:
    """Valid SOOPEX file with empty data block."""
    return """\
%SOOPEX 0.1
%HEADER
format:
  version: "0.1.0"
session:
  start_time: "2026-01-01T00:00:00Z"
  end_time: "2026-01-01T00:01:00Z"
  site_id: "TEST"
  data_source: "simulation"
site:
  approximate_position:
    latitude_deg: 0.0
    longitude_deg: 0.0
    height_m: 0.0
    coordinate_system: "WGS84"
observations:
  type: "raw_doppler"
  doppler_unit: "m/s"
  time_system: "GPST"
  time_format: "gps_seconds"
  columns:
    - epoch
    - norad_id
    - value
orbit_source:
  type: "TLE"
  source: "space-track.org"
  propagator: "SGP4"
%END_HEADER
%DATA
%END_DATA
"""


@pytest.fixture
def invalid_magic_text() -> str:
    """File with invalid magic line."""
    return """\
%RINEX 3.04
%HEADER
format:
  version: "0.1.0"
%END_HEADER
%DATA
%END_DATA
"""


@pytest.fixture
def missing_required_field_text() -> str:
    """File missing required orbit_source field."""
    return """\
%SOOPEX 0.1
%HEADER
format:
  version: "0.1.0"
session:
  start_time: "2026-01-01T00:00:00Z"
  end_time: "2026-01-01T00:01:00Z"
  site_id: "TEST"
  data_source: "simulation"
site:
  approximate_position:
    latitude_deg: 0.0
    longitude_deg: 0.0
    height_m: 0.0
    coordinate_system: "WGS84"
observations:
  type: "raw_doppler"
  doppler_unit: "m/s"
  time_system: "GPST"
  time_format: "gps_seconds"
  columns:
    - epoch
    - norad_id
    - value
%END_HEADER
%DATA
2247264001.000\t54321\t-0.342
%END_DATA
"""
