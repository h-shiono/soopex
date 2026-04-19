"""Roundtrip tests: read → write → read must produce identical results."""

from pathlib import Path

import pandas as pd

import soopex


class TestRoundtrip:
    """Read-write-read identity tests."""

    def test_roundtrip_receiver(self, sample_receiver_path: Path, tmp_soop: Path):
        obs1 = soopex.read(sample_receiver_path)
        obs1.write(tmp_soop)
        obs2 = soopex.read(tmp_soop)
        assert obs1.header == obs2.header
        pd.testing.assert_frame_equal(obs1.data, obs2.data)

    def test_roundtrip_simulation(self, sample_simulation_path: Path, tmp_soop: Path):
        obs1 = soopex.read(sample_simulation_path)
        obs1.write(tmp_soop)
        obs2 = soopex.read(tmp_soop)
        assert obs1.header == obs2.header
        pd.testing.assert_frame_equal(obs1.data, obs2.data)

    def test_roundtrip_minimal(self, minimal_soop_file: Path, tmp_soop: Path):
        obs1 = soopex.read(minimal_soop_file)
        obs1.write(tmp_soop)
        obs2 = soopex.read(tmp_soop)
        assert obs1.header == obs2.header
        pd.testing.assert_frame_equal(obs1.data, obs2.data)

    def test_roundtrip_preserves_column_order(self, sample_receiver_path: Path, tmp_soop: Path):
        obs1 = soopex.read(sample_receiver_path)
        obs1.write(tmp_soop)
        obs2 = soopex.read(tmp_soop)
        assert list(obs1.data.columns) == list(obs2.data.columns)

    def test_roundtrip_preserves_dtypes(self, sample_receiver_path: Path, tmp_soop: Path):
        obs1 = soopex.read(sample_receiver_path)
        obs1.write(tmp_soop)
        obs2 = soopex.read(tmp_soop)
        assert obs1.data.dtypes.equals(obs2.data.dtypes)
