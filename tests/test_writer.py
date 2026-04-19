"""Tests for soopex.writer module."""

import gzip
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import soopex


def _sample_obs(
    columns: list[str] | None = None, data: pd.DataFrame | None = None
) -> soopex.SoopObs:
    cols = columns or ["epoch", "norad_id", "value"]
    df = (
        data
        if data is not None
        else pd.DataFrame(
            {
                "epoch": [2247264001.0, 2247264002.0],
                "norad_id": [54321, 54321],
                "value": [-0.342, -0.358],
            }
        )
    )
    header = soopex.Header(
        format=soopex.FormatInfo(version="0.1.0"),
        session=soopex.Session(
            start_time="2026-01-01T00:00:00Z",
            end_time="2026-01-01T00:00:02Z",
            site_id="TEST",
            data_source="simulation",
        ),
        site=soopex.Site(
            approximate_position=soopex.ApproximatePosition(
                latitude_deg=0.0, longitude_deg=0.0, height_m=0.0
            )
        ),
        observations=soopex.Observations(
            type="raw_doppler",
            doppler_unit="m/s",
            time_system="GPST",
            time_format="gps_seconds",
            columns=cols,
        ),
        orbit_source=soopex.OrbitSource(type="TLE", source="space-track.org", propagator="SGP4"),
    )
    return soopex.SoopObs(header=header, data=df)


class TestWriteBasic:
    """Basic write functionality."""

    def test_write_creates_file(self, tmp_soop: Path):
        _sample_obs().write(tmp_soop)
        assert tmp_soop.exists()

    def test_write_magic_line(self, tmp_soop: Path):
        _sample_obs().write(tmp_soop)
        first_line = tmp_soop.read_text(encoding="utf-8").split("\n")[0]
        assert first_line == "%SOOPEX 0.1"

    def test_write_header_markers(self, tmp_soop: Path):
        _sample_obs().write(tmp_soop)
        text = tmp_soop.read_text(encoding="utf-8")
        assert "%HEADER\n" in text
        assert "%END_HEADER\n" in text

    def test_write_data_markers(self, tmp_soop: Path):
        _sample_obs().write(tmp_soop)
        text = tmp_soop.read_text(encoding="utf-8")
        assert "%DATA\n" in text
        assert text.rstrip().endswith("%END_DATA")


class TestWriteFormatting:
    """TSV formatting rules."""

    def test_epoch_three_decimals(self, tmp_soop: Path):
        _sample_obs().write(tmp_soop)
        text = tmp_soop.read_text(encoding="utf-8")
        data_rows = [
            line
            for line in text.splitlines()
            if line
            and not line.startswith(("%", "#"))
            and "\t" in line
            and not line.startswith((" ", "-"))
            and line.split("\t")[0].replace(".", "").replace("-", "").isdigit()
        ]
        assert data_rows, "no data rows found"
        for row in data_rows:
            epoch_field = row.split("\t")[0]
            decimals = epoch_field.split(".")[1]
            assert len(decimals) == 3, f"epoch {epoch_field!r} should have 3 decimals"

    def test_integer_columns_no_decimal(self, tmp_soop: Path):
        df = pd.DataFrame(
            {
                "epoch": [2247264001.0],
                "norad_id": [54321],
                "value": [-0.342],
                "quality_flag": [0],
            }
        )
        _sample_obs(columns=["epoch", "norad_id", "value", "quality_flag"], data=df).write(tmp_soop)
        text = tmp_soop.read_text(encoding="utf-8")
        last_data_row = [
            line for line in text.splitlines() if line and not line.startswith(("%", "#"))
        ][-1]
        fields = last_data_row.split("\t")
        assert fields[1] == "54321"
        assert fields[3] == "0"

    def test_nan_representation(self, tmp_soop: Path):
        df = pd.DataFrame(
            {
                "epoch": [2247264001.0],
                "norad_id": [54321],
                "value": [np.nan],
            }
        )
        _sample_obs(data=df).write(tmp_soop)
        text = tmp_soop.read_text(encoding="utf-8")
        assert "NaN" in text

    def test_tab_separated(self, tmp_soop: Path):
        _sample_obs().write(tmp_soop)
        text = tmp_soop.read_text(encoding="utf-8")
        data_row = next(
            line
            for line in text.splitlines()
            if line and not line.startswith(("%", "#")) and line[:1].isdigit()
        )
        fields = data_row.split("\t")
        assert len(fields) == 3


class TestWriteGzip:
    """Gzip write support."""

    def test_write_gzip(self, tmp_path: Path):
        gz_path = tmp_path / "test.soop.gz"
        _sample_obs().write(gz_path)
        with gzip.open(gz_path, "rt", encoding="utf-8") as f:
            first = f.readline()
        assert first.startswith("%SOOPEX")


class TestSoopObsMethods:
    """SoopObs select/time_slice/to_dataframe."""

    def test_select_by_norad(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        filtered = obs.select(norad_id=54321)
        assert (filtered.data["norad_id"] == 54321).all()

    def test_time_slice(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        sub = obs.time_slice(2247264002.0, 2247264003.0)
        assert sub.data["epoch"].between(2247264002.0, 2247264003.0).all()

    def test_select_unknown_column_raises(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        with pytest.raises(KeyError):
            obs.select(no_such_column=1)
