"""Tests for soopex.reader module."""

import gzip
from pathlib import Path

import pytest

import soopex
from soopex.reader import SoopexFormatError


class TestMagicLine:
    """Tests for magic line parsing."""

    def test_valid_magic_line(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        assert obs.header.format.version == "0.1.0"

    def test_invalid_magic_line(self, tmp_path: Path, invalid_magic_text: str):
        p = tmp_path / "bad.soop"
        p.write_text(invalid_magic_text, encoding="utf-8")
        with pytest.raises(SoopexFormatError):
            soopex.read(p)

    def test_version_extraction(self, minimal_soop_file: Path):
        obs = soopex.read(minimal_soop_file)
        assert obs.header.format.version == "0.1.0"


class TestHeaderParsing:
    """Tests for YAML header parsing."""

    def test_required_fields_present(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        assert obs.header.session.site_id == "TMS1"
        assert obs.header.site.approximate_position.latitude_deg == pytest.approx(35.6654)
        assert obs.header.observations.type == "dd"
        assert obs.header.orbit_source.type == "TLE"

    def test_optional_fields(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        assert obs.header.receiver.sdr.type == "HackRF One"
        assert obs.header.gnss_reference.receiver_type == "Septentrio mosaic-X5"
        assert obs.header.processing.azel_source.method == "sgp4_from_tle"

    def test_missing_optional_fields(self, minimal_soop_file: Path):
        obs = soopex.read(minimal_soop_file)
        assert obs.header.receiver is None
        assert obs.header.gnss_reference is None

    def test_unknown_fields_ignored(self, tmp_path: Path, minimal_soop_text: str):
        text = minimal_soop_text.replace(
            "orbit_source:",
            "future_field:\n  key: value\norbit_source:",
        )
        p = tmp_path / "future.soop"
        p.write_text(text, encoding="utf-8")
        obs = soopex.read(p)
        assert obs.header.session.site_id == "TEST"

    def test_comments_parsed(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        assert obs.header.comments is not None
        assert len(obs.header.comments) == 2


class TestDataParsing:
    """Tests for TSV data block parsing."""

    def test_dataframe_shape(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        assert len(obs.data) == 8
        assert list(obs.data.columns) == obs.header.observations.columns

    def test_column_types(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        assert obs.data["epoch"].dtype == "float64"
        assert obs.data["norad_id"].dtype == "int64"
        assert obs.data["sat_id"].dtype == "object"

    def test_empty_data_block(self, tmp_path: Path, empty_data_soop_text: str):
        p = tmp_path / "empty.soop"
        p.write_text(empty_data_soop_text, encoding="utf-8")
        obs = soopex.read(p)
        assert len(obs.data) == 0
        assert list(obs.data.columns) == ["epoch", "norad_id", "value"]

    def test_comment_lines_skipped(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        assert (obs.data["epoch"] > 0).all()

    def test_eof_without_end_data(self, tmp_path: Path, minimal_soop_text: str):
        text = minimal_soop_text.replace("%END_DATA\n", "")
        p = tmp_path / "no_end.soop"
        p.write_text(text, encoding="utf-8")
        obs = soopex.read(p)
        assert len(obs.data) == 2

    def test_multiple_satellites_same_epoch(self, sample_receiver_path: Path):
        obs = soopex.read(sample_receiver_path)
        epoch_3 = obs.data[obs.data["epoch"] == 2247264003.0]
        assert len(epoch_3) == 2
        assert set(epoch_3["norad_id"]) == {54321, 55432}


class TestGzipSupport:
    """Tests for transparent .soop.gz handling."""

    def test_read_gzip(self, sample_receiver_path: Path, tmp_path: Path):
        gz_path = tmp_path / "test.soop.gz"
        with (
            open(sample_receiver_path, "rb") as f_in,
            gzip.open(gz_path, "wb") as f_out,
        ):
            f_out.write(f_in.read())
        obs = soopex.read(gz_path)
        assert len(obs.data) == 8


class TestEdgeCases:
    """Edge case tests."""

    def test_crlf_line_endings(self, tmp_path: Path, minimal_soop_text: str):
        text = minimal_soop_text.replace("\n", "\r\n")
        p = tmp_path / "crlf.soop"
        p.write_bytes(text.encode("utf-8"))
        obs = soopex.read(p)
        assert len(obs.data) == 2

    def test_bom_stripped(self, tmp_path: Path, minimal_soop_text: str):
        p = tmp_path / "bom.soop"
        p.write_bytes(b"\xef\xbb\xbf" + minimal_soop_text.encode("utf-8"))
        obs = soopex.read(p)
        assert obs.header.format.version == "0.1.0"
