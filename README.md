# SOOPEX

**Signals of Opportunity Observation Exchange Format**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX) -->

SOOPEX is an open format for storing and exchanging Doppler observables extracted from non-cooperative LEO satellite signals. As RINEX provides a standard exchange format for GNSS observables, SOOPEX provides an exchange format for Signals of Opportunity (SoOp) observables.

> **Status:** This project is in early development (v0.1.0-draft). The specification is subject to breaking changes until v1.0. Feedback and contributions are welcome via [GitHub Issues](../../issues).

## Overview

### Why SOOPEX?

LEO satellite Signals of Opportunity (SoOp) positioning is a rapidly growing research area, but there is no standard exchange format for SoOp observables. Each research group uses proprietary data formats, making reproducibility and cross-validation difficult. SOOPEX aims to fill this gap.

### Key Features

- **RINEX-aligned**: Naming conventions, time systems, and station identifiers are compatible with RINEX 3/4
- **Text-based**: Human-readable, Git-manageable, diff-friendly
- **YAML header + TSV data**: Rich metadata with immediate pandas/numpy ingestibility
- **Constellation-agnostic**: Starlink, Iridium, OneWeb, Orbcomm, and more
- **Frequency-band-agnostic**: Ku, L, VHF, S, Ka bands

## Repository Structure

```
soopex/
├── spec/
│   └── SOOPEX_SPEC_v0.1.md      # Format specification (Draft v0.1)
├── src/
│   └── soopex/                   # Python package
│       ├── __init__.py
│       ├── reader.py             # SOOPEX file reader
│       ├── writer.py             # SOOPEX file writer
│       ├── validator.py          # Header/data validation
│       └── models.py             # Data models (Header, Session, Site, etc.)
├── examples/
│   ├── sample_receiver.soop      # Sample: receiver data
│   └── sample_simulation.soop    # Sample: simulated data
├── tests/
├── pyproject.toml
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

## Quick Start

### Reading a SOOPEX file

```python
import soopex

obs = soopex.read("data.soop")

# Access header metadata
print(obs.header.session.start_time)
print(obs.header.receiver.sdr.type)

# Access data as pandas DataFrame
df = obs.data
print(df.columns)  # ['epoch', 'sat_id', 'norad_id', ...]

# Filter by satellite
starlink = obs.select(norad_id=54321)

# Filter by time range (GPS seconds for the default time_format="gps_seconds")
subset = obs.time_slice(2247264000.0, 2247265800.0)
```

### Writing a SOOPEX file

```python
import soopex
import pandas as pd

header = soopex.Header(
    format=soopex.FormatInfo(version="0.1.0"),
    session=soopex.Session(
        start_time="2026-03-15T03:00:00Z",
        end_time="2026-03-15T04:00:00Z",
        site_id="TMS1",
        data_source="simulation",
    ),
    site=soopex.Site(
        approximate_position=soopex.ApproximatePosition(
            latitude_deg=35.6654, longitude_deg=139.7960, height_m=45.2
        ),
    ),
    observations=soopex.Observations(
        type="dd",
        diff_interval_s=1.0,
        doppler_unit="m/s",
        time_system="GPST",
        time_format="gps_seconds",
        columns=["epoch", "sat_id", "norad_id", "constellation",
                 "azimuth_deg", "elevation_deg", "value", "sigma", "cn0_dBHz"],
    ),
    orbit_source=soopex.OrbitSource(
        type="TLE", source="space-track.org", propagator="SGP4"
    ),
)

data = pd.DataFrame({
    "epoch": [2247264001.0, 2247264002.0],
    "sat_id": ["STARLINK-1234", "STARLINK-1234"],
    "norad_id": [54321, 54321],
    "constellation": ["STARLINK", "STARLINK"],
    "azimuth_deg": [180.3, 180.5],
    "elevation_deg": [78.2, 78.0],
    "value": [-0.342, -0.358],
    "sigma": [0.15, 0.16],
    "cn0_dBHz": [25.3, 24.8],
})

obs = soopex.SoopObs(header=header, data=data)
obs.write("output.soop")  # .soop.gz for gzip
```

### Validating a SOOPEX file

```python
import soopex

result = soopex.validate("data.soop")
if result.is_valid:
    print("File is valid")
else:
    for error in result.errors:
        print(f"  {error}")
```

## Installation

```bash
pip install soopex
```

**Requirements:** Python ≥ 3.10, pandas, numpy, pydantic, ruamel.yaml

## Specification

The full format specification is available at [`spec/SOOPEX_SPEC_v0.1.md`](spec/SOOPEX_SPEC_v0.1.md).

## Related Projects

- [MRTKLIB](https://github.com/h-shiono/mrtklib) — Modernized RTKLIB with CLAS and MADOCA-PPP support
- [RTKLIB](https://github.com/tomojitakasu/RTKLIB) — Open-source GNSS positioning engine

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. We especially welcome:

- Feedback on the specification via [GitHub Issues](../../issues)
- Test data from different receiver/SDR setups
- Parser implementations in other languages (C, MATLAB, Julia, etc.)

## Citation

If you use SOOPEX in your research, please cite:

```bibtex
@software{shiono2026soopex,
  author    = {Shiono, Hayato},
  title     = {{SOOPEX}: Signals of Opportunity Observation Exchange Format},
  year      = {2026},
  url       = {https://github.com/h-shiono/soopex},
  note      = {Draft Specification v0.1}
}
```

<!-- Update with Zenodo DOI once available -->

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
