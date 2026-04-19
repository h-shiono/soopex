"""Roundtrip tests: read → write → read must produce identical results."""

from pathlib import Path


class TestRoundtrip:
    """Read-write-read identity tests."""

    def test_roundtrip_receiver(self, sample_receiver_path: Path, tmp_soop: Path):
        """Receiver file survives roundtrip."""
        # TODO:
        # obs1 = soopex.read(sample_receiver_path)
        # obs1.write(tmp_soop)
        # obs2 = soopex.read(tmp_soop)
        # assert obs1.header == obs2.header
        # pd.testing.assert_frame_equal(obs1.data, obs2.data)
        pass

    def test_roundtrip_simulation(self, sample_simulation_path: Path, tmp_soop: Path):
        """Simulation file survives roundtrip."""
        # TODO: same pattern as above
        pass

    def test_roundtrip_minimal(self, minimal_soop_file: Path, tmp_soop: Path):
        """Minimal file survives roundtrip."""
        # TODO
        pass

    def test_roundtrip_preserves_column_order(self, sample_receiver_path: Path, tmp_soop: Path):
        """Column order is preserved through roundtrip."""
        # TODO:
        # obs1 = soopex.read(sample_receiver_path)
        # obs1.write(tmp_soop)
        # obs2 = soopex.read(tmp_soop)
        # assert list(obs1.data.columns) == list(obs2.data.columns)
        pass

    def test_roundtrip_preserves_dtypes(self, sample_receiver_path: Path, tmp_soop: Path):
        """Column dtypes are preserved through roundtrip."""
        # TODO
        pass
