"""Quickstart example for the soopex package.

Usage:
    uv run python examples/quickstart.py
"""

from pathlib import Path

import pandas as pd

import soopex

EXAMPLE_DIR = Path(__file__).parent


def read_example() -> soopex.SoopObs:
    path = EXAMPLE_DIR / "sample_receiver.soop"
    print(f"Reading: {path}")

    obs = soopex.read(path)
    print(f"  Site:          {obs.header.session.site_id}")
    print(f"  Time window:   {obs.header.session.start_time} → {obs.header.session.end_time}")
    print(f"  Observation:   {obs.header.observations.type}")
    print(f"  Orbit source:  {obs.header.orbit_source.type} ({obs.header.orbit_source.source})")
    print(f"  Rows:          {len(obs.data)}")
    print(f"  Satellites:    {obs.data['norad_id'].nunique()}")
    print(f"  Columns:       {list(obs.data.columns)}")

    sat = obs.select(norad_id=54321)
    print(f"  NORAD 54321:   {len(sat.data)} observations")

    window = obs.time_slice(2247264002.0, 2247264004.0)
    print(f"  Time slice:    {len(window.data)} observations in [t+1, t+3]")

    return obs


def validate_example() -> None:
    path = EXAMPLE_DIR / "sample_receiver.soop"
    print(f"\nValidating: {path}")

    result = soopex.validate(path)
    status = "valid" if result.is_valid else "invalid"
    print(f"  Result: {status}")
    for err in result.errors:
        print(f"    error:   {err}")
    for warn in result.warnings:
        print(f"    warning: {warn}")


def write_example(tmp_path: Path = Path("/tmp")) -> None:
    out = tmp_path / "quickstart_output.soop"
    print(f"\nWriting synthetic data to: {out}")

    header = soopex.Header(
        format=soopex.FormatInfo(version="0.1.0", generator="quickstart"),
        session=soopex.Session(
            start_time="2026-03-15T03:00:00Z",
            end_time="2026-03-15T03:00:02Z",
            site_id="DEMO",
            data_source="simulation",
        ),
        site=soopex.Site(
            approximate_position=soopex.ApproximatePosition(
                latitude_deg=35.6654,
                longitude_deg=139.7960,
                height_m=45.2,
            ),
        ),
        observations=soopex.Observations(
            type="raw_doppler",
            doppler_unit="m/s",
            time_system="GPST",
            time_format="gps_seconds",
            columns=["epoch", "norad_id", "value"],
        ),
        orbit_source=soopex.OrbitSource(type="TLE", source="space-track.org", propagator="SGP4"),
    )
    data = pd.DataFrame(
        {
            "epoch": [2247264001.0, 2247264002.0],
            "norad_id": [54321, 54321],
            "value": [-2845.123, -2831.987],
        }
    )
    soopex.SoopObs(header=header, data=data).write(out)
    print(f"  Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    read_example()
    validate_example()
    write_example()
