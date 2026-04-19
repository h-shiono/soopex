# CLAUDE.md — SOOPEX Development Context

## Project Overview

SOOPEX (Signals of Opportunity Observation Exchange Format) is a specification + Python toolkit for exchanging Doppler observables from non-cooperative LEO satellite signals. This is the reference implementation.

**Repository:** `soopex`  
**License:** Apache-2.0  
**Python:** ≥ 3.10  
**Package manager:** uv (preferred) or pip

## Architecture

```
soopex/
├── spec/
│   └── SOOPEX_SPEC_v0.1.md       # Authoritative format specification
├── soopex/                        # Python package (src layout NOT used; flat)
│   ├── __init__.py                # Public API: read, write, validate, SoopObs, Header, ...
│   ├── models.py                  # Pydantic v2 data models for header sections
│   ├── reader.py                  # .soop file parser
│   ├── writer.py                  # .soop file writer
│   ├── validator.py               # Schema validation (header + data)
│   ├── align.py                   # RINEX time alignment utility
│   └── _version.py                # Version string ("0.1.0a1")
├── examples/
│   ├── sample_receiver.soop       # Example: real receiver data
│   ├── sample_simulation.soop     # Example: simulated data
│   └── quickstart.py              # Minimal usage example
├── tests/
│   ├── test_reader.py
│   ├── test_writer.py
│   ├── test_validator.py
│   ├── test_roundtrip.py          # Read → write → read identity test
│   └── conftest.py                # Shared fixtures (sample .soop files)
├── pyproject.toml
├── LICENSE                        # Apache-2.0
├── README.md
├── CONTRIBUTING.md
└── CLAUDE.md                      # This file
```

## Key Design Decisions

1. **Pydantic v2 for models** — Header sections (Session, Site, Observations, etc.) are Pydantic BaseModel classes. This gives us validation, serialization, and IDE support for free.

2. **pandas DataFrame for data** — The TSV data block maps directly to a DataFrame. Column types are enforced on read (norad_id → int, epoch → float64, etc.).

3. **YAML round-trip with ruamel.yaml** — Use ruamel.yaml (not PyYAML) to preserve comments and formatting in headers during read-modify-write operations.

4. **No external GNSS dependencies** — The core package depends only on pandas, numpy, pydantic, and ruamel.yaml. Optional dependencies (sgp4, skyfield) are for simulation/utility features only.

5. **gzip transparency** — `soopex.read()` auto-detects `.soop.gz` and decompresses transparently.

## Dependencies

### Core (required)
```
pandas >= 2.0
numpy >= 1.24
pydantic >= 2.0
ruamel.yaml >= 0.18
```

### Optional (for simulation / utilities)
```
sgp4 >= 2.22          # TLE propagation
skyfield >= 1.45      # High-accuracy satellite positions
georinex >= 1.16      # RINEX file reading (for align)
```

## Implementation Notes

### File Parsing (`reader.py`)

The parser operates in three phases:

1. **Magic line**: Read first line, verify `%SOOPEX <version>`, extract version
2. **Header**: Extract text between `%HEADER` and `%END_HEADER`, parse as YAML, validate against Pydantic models
3. **Data**: Read from `%DATA` to `%END_DATA`/EOF as TSV into DataFrame. Skip comment lines (`#`). Apply column types from header `observations.columns`.

```python
# Target API
obs = soopex.read("file.soop")
# Returns SoopObs(header=Header(...), data=pd.DataFrame(...))
```

Edge cases to handle:
- Missing `%END_DATA` (treat EOF as end)
- BOM at file start (strip if present)
- CR+LF line endings (normalize to LF)
- Empty data block (valid; returns empty DataFrame with correct columns)

### File Writing (`writer.py`)

```python
obs.write("output.soop")
# Writes: magic line → %HEADER → YAML → %END_HEADER → %DATA → TSV → %END_DATA
```

TSV formatting rules:
- float64: 3 decimal places for epoch, az, el; variable for value/sigma
- int columns: no decimal point
- string columns: as-is (no quoting)
- NaN: literal string "NaN"

### Validation (`validator.py`)

Two levels:
1. **Schema validation**: Header required fields present, types correct
2. **Semantic validation**: Column count matches header `columns` list, norad_id are positive integers, epoch is monotonically non-decreasing per satellite, az/el in valid ranges

```python
result = soopex.validate("file.soop")
# Returns ValidationResult(is_valid=bool, errors=list[str], warnings=list[str])
```

### Data Models (`models.py`)

```python
class Header(BaseModel):
    format: FormatInfo
    session: Session
    site: Site
    observations: Observations
    orbit_source: OrbitSource
    receiver: Optional[Receiver] = None
    gnss_reference: Optional[GnssReference] = None
    processing: Optional[Processing] = None
    simulation: Optional[Simulation] = None
    comments: Optional[list[str]] = None
    extensions: Optional[dict] = None

class SoopObs:
    header: Header
    data: pd.DataFrame
    
    def select(self, **kwargs) -> "SoopObs": ...
    def time_slice(self, start, end) -> "SoopObs": ...
    def to_dataframe(self) -> pd.DataFrame: ...  # data with header metadata as attrs
```

### RINEX Alignment (`align.py`)

```python
merged = soopex.align(gnss_rinex_path, soop_path, tolerance_s=0.5)
# Time-aligns GNSS and SoOp observations
# Returns AlignedObs with .gnss_epochs, .soop_epochs, .merged
```

This requires `georinex` as optional dependency. Raise `ImportError` with clear message if not installed.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=soopex --cov-report=term-missing
```

### Test Strategy

- **Unit tests**: Each module (reader, writer, validator, models) tested independently
- **Roundtrip test**: `read(write(obs)) == obs` for various configurations
- **Edge cases**: Empty files, missing optional fields, unknown columns, large files
- **Sample files**: Use files from `examples/` as integration test fixtures

## Code Style

- Format with `ruff format`
- Lint with `ruff check`
- Type annotations on all public APIs
- Docstrings: Google style
- No print statements; use `logging` module

## Version Scheme

- Package version: `0.1.0a1` (alpha), `0.1.0b1` (beta), `0.1.0` (release)
- Follows the specification version (spec v0.1 → package v0.1.x)

## Scope for v0.1.0-alpha

### In scope (Tier 1)
- [ ] `soopex.read()` — Parse .soop files to SoopObs
- [ ] `soopex.write()` — Write SoopObs to .soop files
- [ ] `soopex.validate()` — Validate .soop files
- [ ] Pydantic models for all header sections
- [ ] .soop.gz transparent read/write
- [ ] Sample .soop files
- [ ] Unit tests with >80% coverage

### Deferred (Tier 2 — v0.2.0)
- [ ] `soopex.simulate()` — Generate synthetic Doppler from TLE+SGP4
- [ ] Clock noise model injection (OCXO, TCXO, free-running)
- [ ] `soopex.align()` — RINEX time alignment

### Deferred (Tier 3 — v0.3.0+)
- [ ] Sky plot visualization
- [ ] Doppler time series plotting
- [ ] C/N₀ heatmap
- [ ] Satellite visibility timeline

## Build and Release

```bash
# Build
uv build

# Publish to PyPI
uv publish

# Create GitHub Release (triggers Zenodo DOI)
gh release create v0.1.0-alpha --title "v0.1.0-alpha" --notes "Initial alpha release"
```

## Context: Related Projects

- **MRTKLIB**: Modernized RTKLIB fork by the same author. SOOPEX files will be consumed by MRTKLIB as additional observation input for GNSS+SoOp hybrid positioning.
- **CLASLIB**: CLAS processing library. MRTKLIB's PPP-RTK engine.
- **MADOCALIB**: MADOCA-PPP processing library.

## Context: Research Background

This toolkit supports research on LEO SoOp-enhanced GNSS positioning — using Doppler observables from non-cooperative LEO satellite signals (e.g., Starlink) to improve PPP and PPP-RTK performance. See the associated publications for technical details.
