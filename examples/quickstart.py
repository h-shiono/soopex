"""Quickstart example for the soopex package.

Usage:
    python examples/quickstart.py
"""

from pathlib import Path

# import soopex  # Uncomment when package is implemented

EXAMPLE_DIR = Path(__file__).parent


def read_example():
    """Read a SOOPEX file and inspect its contents."""
    path = EXAMPLE_DIR / "sample_receiver.soop"
    print(f"Reading: {path}")

    # obs = soopex.read(path)
    #
    # # Header metadata
    # print(f"  Site: {obs.header.session.site_id}")
    # print(f"  Time: {obs.header.session.start_time} → {obs.header.session.end_time}")
    # print(f"  Type: {obs.header.observations.type}")
    # print(f"  Orbit: {obs.header.orbit_source.type} ({obs.header.orbit_source.source})")
    #
    # # Data summary
    # print(f"  Rows: {len(obs.data)}")
    # print(f"  Satellites: {obs.data['norad_id'].nunique()}")
    # print(f"  Columns: {list(obs.data.columns)}")
    #
    # # Filter by satellite
    # sat = obs.select(norad_id=54321)
    # print(f"  NORAD 54321: {len(sat.data)} observations")

    print("  [soopex package not yet implemented — see CLAUDE.md]")


def validate_example():
    """Validate a SOOPEX file."""
    path = EXAMPLE_DIR / "sample_receiver.soop"
    print(f"\nValidating: {path}")

    # result = soopex.validate(path)
    # if result.is_valid:
    #     print("  ✓ File is valid")
    # else:
    #     for error in result.errors:
    #         print(f"  ✗ {error}")
    # for warning in result.warnings:
    #     print(f"  ⚠ {warning}")

    print("  [soopex package not yet implemented — see CLAUDE.md]")


if __name__ == "__main__":
    read_example()
    validate_example()
