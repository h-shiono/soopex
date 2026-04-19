"""Tests for soopex.validator module."""

from pathlib import Path

import soopex


class TestSchemaValidation:
    """Header schema validation tests."""

    def test_valid_file(self, sample_receiver_path: Path):
        result = soopex.validate(sample_receiver_path)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_required_field(self, tmp_path: Path, missing_required_field_text: str):
        p = tmp_path / "bad.soop"
        p.write_text(missing_required_field_text, encoding="utf-8")
        result = soopex.validate(p)
        assert not result.is_valid
        assert any("orbit_source" in e for e in result.errors)

    def test_invalid_observation_type(self, tmp_path: Path, minimal_soop_text: str):
        text = minimal_soop_text.replace('type: "raw_doppler"', 'type: "invalid_type"')
        p = tmp_path / "bad_type.soop"
        p.write_text(text, encoding="utf-8")
        result = soopex.validate(p)
        assert not result.is_valid

    def test_invalid_time_system(self, tmp_path: Path, minimal_soop_text: str):
        text = minimal_soop_text.replace('time_system: "GPST"', 'time_system: "XYZ"')
        p = tmp_path / "bad_time.soop"
        p.write_text(text, encoding="utf-8")
        result = soopex.validate(p)
        assert not result.is_valid


class TestSemanticValidation:
    """Data semantic validation tests."""

    def test_column_count_mismatch(self, tmp_path: Path, minimal_soop_text: str):
        text = minimal_soop_text.replace(
            "2247264001.000\t54321\t-0.342",
            "2247264001.000\t54321\t-0.342\textra",
        )
        p = tmp_path / "extra_col.soop"
        p.write_text(text, encoding="utf-8")
        result = soopex.validate(p)
        assert not result.is_valid

    def test_norad_id_positive(self, tmp_path: Path, minimal_soop_text: str):
        text = minimal_soop_text.replace("54321", "-1")
        p = tmp_path / "neg_norad.soop"
        p.write_text(text, encoding="utf-8")
        result = soopex.validate(p)
        assert not result.is_valid
        assert any("norad_id" in e for e in result.errors)

    def test_azimuth_range(self, sample_receiver_path: Path):
        result = soopex.validate(sample_receiver_path)
        assert result.is_valid

    def test_azimuth_out_of_range(self, sample_receiver_path: Path, tmp_path: Path):
        obs = soopex.read(sample_receiver_path)
        obs.data.loc[0, "azimuth_deg"] = 400.0
        bad = tmp_path / "bad_az.soop"
        obs.write(bad)
        result = soopex.validate(bad)
        assert not result.is_valid
        assert any("azimuth_deg" in e for e in result.errors)

    def test_elevation_range(self, sample_receiver_path: Path):
        result = soopex.validate(sample_receiver_path)
        assert result.is_valid

    def test_elevation_out_of_range(self, sample_receiver_path: Path, tmp_path: Path):
        obs = soopex.read(sample_receiver_path)
        obs.data.loc[0, "elevation_deg"] = 100.0
        bad = tmp_path / "bad_el.soop"
        obs.write(bad)
        result = soopex.validate(bad)
        assert not result.is_valid
        assert any("elevation_deg" in e for e in result.errors)

    def test_epoch_monotonic_per_satellite(self, sample_receiver_path: Path):
        result = soopex.validate(sample_receiver_path)
        assert result.is_valid

    def test_epoch_non_monotonic_detected(self, sample_receiver_path: Path, tmp_path: Path):
        obs = soopex.read(sample_receiver_path)
        # Swap first two epochs for norad_id=54321 to create decreasing order
        obs.data.loc[0, "epoch"] = 2247264009.0
        bad = tmp_path / "bad_epoch.soop"
        obs.write(bad)
        result = soopex.validate(bad)
        assert not result.is_valid
        assert any("epoch" in e for e in result.errors)


class TestValidationResult:
    """ValidationResult interface tests."""

    def test_valid_result_attributes(self, sample_receiver_path: Path):
        result = soopex.validate(sample_receiver_path)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")
        assert hasattr(result, "warnings")

    def test_errors_are_strings(self, tmp_path: Path, missing_required_field_text: str):
        p = tmp_path / "bad.soop"
        p.write_text(missing_required_field_text, encoding="utf-8")
        result = soopex.validate(p)
        assert all(isinstance(e, str) for e in result.errors)
