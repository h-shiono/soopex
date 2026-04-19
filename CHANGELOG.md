# Changelog

All notable changes to SOOPEX (the specification and reference implementation)
are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Spec and package versions are aligned (spec v0.1 ↔ package v0.1.x).

## [Unreleased]

## [0.1.0a1] — 2026-04-19

First public alpha of the SOOPEX reference implementation.

### Added

- **Specification**: `spec/SOOPEX_SPEC_v0.1.md` — initial draft covering magic
  line, YAML header, TSV data block, naming convention, required columns,
  time systems, and extension mechanism.
- **Reader** (`soopex.read`): three-phase parser (magic → YAML header → TSV
  data) with transparent `.soop.gz` decompression, BOM stripping, CRLF
  normalization, and column-name-based dtype coercion.
- **Writer** (`soopex.write`, `SoopObs.write`): emits magic, YAML header via
  `ruamel.yaml`, and TSV data block. `epoch` / `azimuth_deg` /
  `elevation_deg` formatted with 3 decimals; integer columns as integers;
  missing values as literal `NaN`. Paths ending in `.gz` are written
  gzip-compressed.
- **Validator** (`soopex.validate`): two-level validation (Pydantic schema
  for the header; semantic checks for column agreement, `norad_id > 0`,
  `azimuth_deg ∈ [0, 360)`, `elevation_deg ∈ [0, 90]`, per-satellite epoch
  monotonicity). Returns `ValidationResult(is_valid, errors, warnings)`.
- **Models** (`soopex.models`): Pydantic v2 header classes —
  `Header`, `FormatInfo`, `Session`, `Site`, `ApproximatePosition`,
  `Observations`, `OrbitSource`, `Receiver`, `SDR`, `Antenna`,
  `AntennaPointing`, `LNB`, `GnssReference`, `Processing`, `AzelSource`,
  `Simulation`. Conditional validators enforce `type="dd" → diff_interval_s`,
  `type="TLE" → propagator`, and the required-columns contract. Unknown
  fields are preserved (`extra="allow"`) for forward compatibility.
- **SoopObs** container with `select`, `time_slice`, `to_dataframe`, and
  `write` methods.
- **Examples**: `examples/sample_receiver.soop`,
  `examples/sample_simulation.soop` (placeholder values), and a runnable
  `examples/quickstart.py`.
- **Tests**: 48 pytest cases covering reader, writer, validator, and
  round-trip invariants; 90% line coverage.

### Known limitations

- `examples/sample_*.soop` values are illustrative placeholders, not
  physically accurate. They will be regenerated from TLE+SGP4 in a later
  alpha.
- `soopex.align()` and `soopex.simulate()` are declared but not yet
  implemented (scoped for 0.2.0).
- Round-tripping a file through the Pydantic header does not preserve YAML
  formatting (comments, key order) — only the data content is preserved.
- `float` columns other than epoch / az / el are written with `%.6g`
  formatting; round-trip preserves values but not exact string form.

[Unreleased]: https://github.com/h-shiono/soopex/compare/v0.1.0a1...HEAD
[0.1.0a1]: https://github.com/h-shiono/soopex/releases/tag/v0.1.0a1
