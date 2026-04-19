# SOOPEX: Signals of Opportunity Observation Exchange Format

**Version:** 0.1.0-draft  
**Status:** DRAFT — This specification is subject to breaking changes until v1.0.  
**Date:** 2026-04-19  
**Author:** Hayato Shiono (Tokyo University of Marine Science and Technology)  
**License:** Apache-2.0

---

## 1. Introduction

### 1.1 Purpose

SOOPEX (SoOp Observation Exchange Format) is an open format for storing and exchanging Doppler observables extracted from non-cooperative LEO satellite signals. As RINEX provides a standard exchange format for GNSS pseudorange and carrier phase observables, SOOPEX provides an exchange format for Signals of Opportunity (SoOp) observables.

### 1.2 Design Principles

| Principle | Rationale |
|-----------|-----------|
| RINEX coexistence | Aligned naming conventions and time systems with RINEX 3/4. GNSS observables in RINEX, SoOp observables in SOOPEX |
| Text-based | Git-manageable, diff-friendly, human-readable |
| YAML header + TSV data | Flexible metadata extensibility combined with immediate pandas/numpy ingestibility |
| Constellation-agnostic | Unified description for Starlink, Iridium, Orbcomm, OneWeb, Kuiper, etc. |
| Frequency-band-agnostic | Unified description for Ku, L, VHF, S, Ka bands |
| Processing-level separation | Distinct storage for raw Doppler, epoch-differenced Doppler, and raw frequency |
| Minimal required fields | Low entry barrier; optional fields for detailed metadata |

### 1.3 Scope

This specification defines observation exchange for Doppler observables extracted from LEO satellite downlink signals. The initial version (v0.1) is optimized for satellite-borne sources; extension to terrestrial or airborne sources is not prohibited but is outside the scope of the current specification and reference implementation.

**In scope (v0.1):**

- Raw Doppler (`raw_doppler`): Doppler frequency shift from LEO satellites (Hz or m/s)
- Epoch-differenced Doppler (`dd`): Inter-epoch differenced Doppler (m/s)
- Raw frequency (`raw_freq`): Tone frequency time series (Hz)

**Out of scope (future extensions):**

- Carrier phase observations
- Pseudorange observations
- Raw IQ sample data (metadata references only)
- Terrestrial or airborne signal sources

### 1.4 Notation

The keywords MUST, MUST NOT, REQUIRED, SHALL, SHOULD, RECOMMENDED, OPTIONAL in this document follow the interpretation described in RFC 2119.

---

## 2. File Naming Convention

### 2.1 Standard Naming

File names follow the RINEX 3/4 long naming convention with a SoOp-specific data type identifier:

```
SSSSMMCCC_R_YYYYDDDHHMM_PPP_FFF_DO.soop
```

| Field | Width | Description | Example |
|-------|-------|-------------|---------|
| `SSSS` | 4 | Station identifier | `TMS1` |
| `MM` | 2 | Monument number (typically `00`) | `00` |
| `CCC` | 3 | Country code (ISO 3166-1 alpha-3) | `JPN` |
| `R` | 1 | Data source: `R` = Receiver, `S` = Simulation | `R` |
| `YYYY` | 4 | Year | `2026` |
| `DDD` | 3 | Day of year | `074` |
| `HH` | 2 | Start hour (UTC) | `03` |
| `MM` | 2 | Start minute (UTC) | `00` |
| `PPP` | 3 | Duration, following RINEX convention: `01H`, `15M`, `05M`, `30S`, `01D`, etc. | `01H` |
| `FFF` | 3 | Frequency band: `KUB` (Ku), `LBD` (L), `VHF`, `SBD` (S), `MIX` (multiple bands in one file) | `KUB` |
| `DO` | 2 | Data type + observation: `DD` (diff Doppler), `RD` (raw Doppler), `RF` (raw freq) | `DD` |
| `.soop` | — | File extension | `.soop` |

### 2.2 Examples

```
TMS100JPN_R_20260740300_01H_KUB_DD.soop    # Receiver, diff Doppler, Ku-band, 1 hour
TMS100JPN_S_20260740300_01H_KUB_DD.soop    # Simulation
TMS100JPN_R_20260740300_01H_MIX_RD.soop    # Multi-band, raw Doppler
```

### 2.3 Association with RINEX Files

Co-located GNSS RINEX files are linked via the `gnss_reference.rinex_file` header field. Station identifiers (`SSSS`) SHOULD match between SOOPEX and RINEX files for the same site.

---

## 3. File Structure

A SOOPEX file consists of three sections:

```
┌─────────────────────────────────┐
│  Magic Line                     │  "%SOOPEX <MAJOR.MINOR>"
├─────────────────────────────────┤
│  YAML Header Block              │  "%HEADER" ... "%END_HEADER"
│  (metadata, configuration)      │
├─────────────────────────────────┤
│  TSV Data Block                 │  "%DATA" ... "%END_DATA" or EOF
│  (observation records)          │
└─────────────────────────────────┘
```

**Magic line versioning:** The magic line contains `MAJOR.MINOR` only (e.g., `%SOOPEX 0.1`) for parser compatibility determination. The full semantic version including PATCH is specified in `format.version` within the YAML header (e.g., `"0.1.0"`). Parsers MUST use the magic line version to determine compatibility and MAY use `format.version` for detailed version-specific behavior.

- Encoding: UTF-8. A UTF-8 BOM (`U+FEFF`), if present at the start of the file, MUST be ignored by parsers.
- Line endings: LF (`\n`) RECOMMENDED; CR+LF permitted. Parsers MUST accept CR+LF by normalizing to LF. Writers SHOULD emit LF only.
- Trailing content: Content after `%END_DATA`, if present, MUST be ignored by parsers.
- Blank lines: Blank lines anywhere in the file (including within the data block) MUST be ignored by parsers.
- Compression: `.soop.gz` (gzip) is the RECOMMENDED compressed form. Parsers SHOULD support transparent decompression.

---

## 4. Header Specification

### 4.1 Structure

The header is a YAML document enclosed between `%HEADER` and `%END_HEADER` markers:

```yaml
%SOOPEX 0.1
%HEADER
# ... YAML content ...
%END_HEADER
```

### 4.2 Required Fields

#### 4.2.1 `format`

```yaml
format:
  version: "0.1.0"              # REQUIRED: Semantic versioning
  generator: "soopex-tools 0.1" # RECOMMENDED: Generator software name + version
```

#### 4.2.2 `session`

```yaml
session:
  start_time: "2026-03-15T03:00:00Z"   # REQUIRED: ISO 8601, UTC
  end_time: "2026-03-15T04:00:00Z"     # REQUIRED: ISO 8601, UTC
  duration_s: 3600                      # OPTIONAL: Redundant but convenient
  site_id: "TMS1"                       # REQUIRED: 4-character site identifier
  data_source: "receiver"               # REQUIRED: "receiver" | "simulation"
```

#### 4.2.3 `site`

```yaml
site:
  name: "TUMSAT Etchujima Campus"          # RECOMMENDED
  approximate_position:                     # REQUIRED
    latitude_deg: 35.6654                   # WGS84
    longitude_deg: 139.7960                 # WGS84
    height_m: 45.2                          # Ellipsoidal height
    coordinate_system: "WGS84"             # REQUIRED: "WGS84" | "ITRF2020" | ...
```

#### 4.2.4 `observations`

Fields marked "REQUIRED if type=..." are conditionally required: their absence when the condition is met constitutes a validation error, not merely a recommendation.

```yaml
observations:
  type: "dd"                    # REQUIRED: "dd" | "raw_doppler" | "raw_freq"
  diff_interval_s: 1.0          # REQUIRED if type=dd: Differencing interval (s)
  doppler_unit: "m/s"           # REQUIRED if type=dd|raw_doppler: "m/s" | "Hz"
  frequency_unit: "Hz"          # REQUIRED if type=raw_freq
  reference_frequency_hz: 11325000000  # RECOMMENDED: Nominal carrier frequency
  time_system: "GPST"           # REQUIRED: "GPST" | "UTC" | "TAI"
  time_format: "gps_seconds"    # REQUIRED: "gps_seconds" | "iso8601" | "unix"
  columns:                      # REQUIRED: Data column definitions (see §5)
    - epoch
    - sat_id
    - norad_id
    - constellation
    - azimuth_deg
    - elevation_deg
    - value
    - sigma
    - cn0_dBHz
```

#### 4.2.5 `orbit_source`

```yaml
orbit_source:                          # REQUIRED
  type: "TLE"                          # REQUIRED: "TLE" | "SP3" | "broadcast" | "operator"
  source: "space-track.org"            # REQUIRED: Data source
  propagator: "SGP4"                   # OPTIONAL: Default "SGP4" if type=TLE
  tle_file: "starlink_20260315.tle"    # RECOMMENDED: Associated TLE file
  sp3_file: null                       # RECOMMENDED if type=SP3
  epoch_age_max_h: 24                  # RECOMMENDED: Maximum TLE age used (hours)
```

### 4.3 Optional Fields

#### 4.3.1 `receiver` (for measured data)

```yaml
receiver:
  sdr:
    type: "HackRF One"
    serial: "0000000000000000"
    firmware: "2024.02.1"
    sampling_rate_hz: 2000000
    sample_bits: 8
    bandwidth_hz: 2000000
  antenna:
    type: "parabolic_dish+LNBF"
    dish_diameter_m: 0.45
    gain_dBi: 33.0                     # OPTIONAL: Estimated antenna gain
    pointing:
      mode: "fixed"                    # "fixed" | "tracking" | "scanning"
      azimuth_deg: 0.0                 # If fixed
      elevation_deg: 90.0             # If fixed
    lnb:
      type: "qro.cz SDR TCXO"
      lo_frequency_hz: 9750000000
      lo_stability: "tcxo"            # "tcxo" | "pll" | "free_running"
      lo_stability_ppm: 2.0           # OPTIONAL: Estimated LO stability
```

#### 4.3.2 `gnss_reference`

```yaml
gnss_reference:
  rinex_file: "TMS100JPN_R_20260740300_01H_MN.rnx"
  receiver_type: "Septentrio mosaic-X5"
  time_sync_method: "pps"              # "pps" | "software_ntp" | "none"
  time_sync_accuracy_s: 0.000001       # Estimated synchronization accuracy
```

#### 4.3.3 `processing`

```yaml
processing:
  doppler_extraction:
    method: "fft_peak_tracking"        # "fft_peak_tracking" | "pll" | "cross_correlation"
    fft_size: 65536
    coherent_integration_s: 0.032      # CPI duration
  satellite_identification:
    method: "sgp4_doppler_matching"    # "sgp4_doppler_matching" | "beam_id" | "manual"
    matching_threshold_hz: 500
  lo_drift_correction:
    method: "epoch_differencing"       # "epoch_differencing" | "gps_disciplined" | "none"
  azel_source:                         # RECOMMENDED: Provenance of az/el columns
    method: "sgp4_from_tle"            # "sgp4_from_tle" | "precise_orbit" | "tracked"
    reference: "orbit_source"          # Which orbit source was used
  quality_control:
    cn0_mask_dBHz: 15.0
    elevation_mask_deg: 10.0
```

#### 4.3.4 `simulation` (for simulated data)

```yaml
simulation:
  software: "soopex-sim 0.1.0"
  constellation_model: "starlink_gen2_phase1"
  num_satellites: 4408
  doppler_noise:
    model: "gaussian"
    sigma_m_s: 0.01
  clock_model:
    type: "free_running_lnb"
    drift_rate_m_s_sqrt_s: 0.7
    initial_bias_hz: 0.0
  ionospheric_model: "none"           # Ku-band: negligible (1/52 of L1)
  tropospheric_model: "none"          # Optional: "saastamoinen" | "vmf3"
```

#### 4.3.5 `comments`

```yaml
comments:
  - "Clear sky, no interference detected"
  - "LNB warm-up period: first 300 s excluded"
```

---

## 5. Data Block Specification

### 5.1 Structure

The data block begins with `%DATA` and ends with `%END_DATA` or EOF. Data records are TSV (tab-separated values).

```
%DATA
# epoch          sat_id           norad_id  constellation  az      el     value    sigma  cn0    tone  qf
2247264001.000	STARLINK-1234	54321	STARLINK	180.3	78.2	-0.342	0.15	25.3	4	0
```

Lines beginning with `#` within the data block are comments and MUST be ignored by parsers.

**TSV formatting rules:**

- Fields are separated by a single horizontal tab character (`\t`, U+0009). Multiple consecutive tabs represent empty fields.
- Leading and trailing whitespace within fields MUST NOT be trimmed by parsers, as string fields (e.g., `sat_id`) may legitimately contain spaces.
- Missing numeric values MUST be represented as the literal string `NaN` (case-sensitive) by writers. Parsers SHOULD accept common casings (`nan`, `NAN`) for interoperability but MAY issue a warning.
- Missing string values MUST be represented as an empty string (two consecutive tabs).

**Column contract:** The `observations.columns` array in the header defines the exact set and order of columns in the TSV data block. This array MUST contain at least the required columns for the chosen `observations.type` (see §5.2.1). The order of entries in `observations.columns` MUST exactly match the order of fields in each data row.

**Sort order:** Data rows SHOULD be sorted by `epoch` in ascending order. Within the same epoch, row order is unspecified. Parsers SHOULD NOT assume any particular ordering within an epoch.

### 5.2 Column Definitions

#### 5.2.1 Required Columns

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `epoch` | float64 | per `time_format` | Observation epoch |
| `norad_id` | int | — | NORAD catalog number (primary satellite key) |
| `value` | float64 | per `doppler_unit` or `frequency_unit` | Observation value |

#### 5.2.2 Recommended Columns

`norad_id` is the primary satellite key used for data processing and cross-referencing with TLE catalogs. `sat_id` is a human-readable alias provided for convenience; it MUST NOT be used as a primary key, as satellite names may change over time.

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `sat_id` | string | — | Human-readable satellite name (e.g., "STARLINK-1234") |
| `constellation` | string | — | Constellation identifier (see §5.3) |
| `azimuth_deg` | float64 | degrees | Azimuth of satellite at observation epoch (0–360, clockwise from North). See `processing.azel_source` for provenance |
| `elevation_deg` | float64 | degrees | Elevation of satellite at observation epoch (0–90). See `processing.azel_source` for provenance |
| `sigma` | float64 | same as `value` | Estimated standard deviation of observation |
| `cn0_dBHz` | float64 | dB-Hz | Carrier-to-noise density ratio |

#### 5.2.3 Optional Columns

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `tone_index` | int | — | Index of tracked tone within signal (e.g., 0–8 for Starlink 9-tone) |
| `quality_flag` | int | — | Quality indicator: 0 = nominal, 1 = marginal, 2 = degraded, ≥10 = user-defined |
| `range_rate_m_s` | float64 | m/s | Geometric range rate (computed, not observed) |
| `doppler_rate_hz_s` | float64 | Hz/s | Doppler frequency rate |
| `frequency_hz` | float64 | Hz | Absolute tracked frequency (before Doppler extraction) |
| `lo_bias_hz` | float64 | Hz | Estimated LO frequency bias at epoch |
| `operator_sat_id` | string | — | Operator-specific satellite identifier (e.g., SpaceX internal ID) |

### 5.3 Constellation Identifiers

| Identifier | Constellation |
|------------|--------------|
| `STARLINK` | SpaceX Starlink |
| `ONEWEB` | OneWeb |
| `IRIDIUM` | Iridium / Iridium NEXT |
| `ORBCOMM` | Orbcomm |
| `GLOBALSTAR` | Globalstar |
| `KUIPER` | Amazon Kuiper |
| `OTHER` | Other / unidentified |

New identifiers MAY be added in minor version updates. Parsers MUST accept unknown constellation identifiers without error.

### 5.4 Missing Data

Missing or unavailable values MUST be represented as `NaN` (case-sensitive) for floating-point columns and as an empty string (consecutive tab characters) for string columns. Integer columns with missing values MAY be handled by any of: (a) using `-1` as a sentinel where semantically unambiguous, (b) promoting the column to float64 and using `NaN`, or (c) using a nullable-integer type (e.g., pandas `Int64`). Epoch gaps (missing observations) are represented by absence of rows; no explicit gap markers are used.

### 5.5 Azimuth / Elevation Semantics

The `azimuth_deg` and `elevation_deg` columns record the satellite direction as computed at observation time. These values represent a snapshot of the observer's best knowledge of satellite geometry when the observation was made.

When precise orbits become available after the fact, processing software SHOULD recompute az/el from precise ephemerides rather than relying on these stored values. However, stored values MUST NOT be overwritten in the original SOOPEX file; recomputed values should be used only within the processing pipeline.

The provenance of stored az/el values is declared in the `processing.azel_source` header field:

- `sgp4_from_tle`: Computed from TLE via SGP4 propagation (typical accuracy: ~0.1° for fresh TLE)
- `precise_orbit`: Computed from SP3 or equivalent precise orbit product
- `tracked`: Reported directly by the receiver or SDR tracking loop, reflecting the antenna pointing or beam steering direction as determined by the hardware during signal acquisition

---

## 6. Time Systems

### 6.1 Supported Time Formats

| Format | Description | Example |
|--------|-------------|---------|
| `gps_seconds` | Continuous GPS seconds (no leap seconds) | `2247264001.000` |
| `iso8601` | ISO 8601 UTC string | `2026-03-15T03:00:01.000Z` |
| `unix` | UNIX timestamp (UTC, with leap seconds) | `1773640801.000` |

### 6.2 Recommendations

- `gps_seconds` is RECOMMENDED for maximum GNSS interoperability
- The `time_system` field specifies the reference time scale
- Parsers MUST preserve the declared `time_system` and `time_format` as-is; time-scale conversions (e.g., GPST ↔ UTC including leap-second corrections) are the responsibility of downstream processing software, not the SOOPEX parser

---

## 7. Versioning Policy

SOOPEX follows Semantic Versioning 2.0.0:

- **MAJOR** (1.0, 2.0, ...): Backward-incompatible changes. Parser updates required.
- **MINOR** (0.1, 0.2, ...): Backward-compatible additions (new constellations, new optional columns, etc.)
- **PATCH** (0.1.1, 0.1.2, ...): Clarifications, errata

**Compatibility rules:**

- Parsers MUST read any file within the same MAJOR version
- Parsers MUST ignore unknown optional fields at any nesting depth (forward compatibility). This rule applies to all unknown keys, not only those under the `extensions` section (see §9).
- Adding required fields constitutes a MAJOR version change

---

## 8. Relationship to Existing Formats

| Format | Relationship |
|--------|-------------|
| **RINEX 3/4** | Coexistence. Aligned naming and time systems. GNSS observables in RINEX; SoOp observables in SOOPEX |
| **SP3** | Precise satellite orbits. Referenced via `orbit_source.sp3_file` |
| **TLE / 3LE** | Standard LEO orbit source. Referenced via `orbit_source.tle_file` |
| **SigMF** | Signal metadata format for raw IQ. Complementary: SigMF for IQ, SOOPEX for extracted observables |
| **SBF / UBX** | Proprietary receiver binary formats. SOOPEX is receiver-independent |

---

## 9. Extension Mechanism

Future extensions are accommodated via the reserved `extensions` header section:

```yaml
extensions:
  carrier_phase:
    enabled: false
    note: "Future: LEO carrier phase observations"
  pseudorange:
    enabled: false
    note: "Future: Cooperative LEO pseudorange"
  multi_receiver:
    enabled: false
    note: "Future: Multiple SDR receivers for beam forming"
```

Extension schemas are defined in MAJOR version updates. Parsers MUST ignore unknown extensions. The `extensions` section is a convention for opt-in experimental features; the general forward-compatibility rule (§7) applies independently to all unknown keys throughout the header.

---

## 10. Complete File Example

```
%SOOPEX 0.1
%HEADER
format:
  version: "0.1.0"
  generator: "soopex-tools 0.1.0"
session:
  start_time: "2026-03-15T03:00:00Z"
  end_time: "2026-03-15T03:05:00Z"
  site_id: "TMS1"
  data_source: "receiver"
site:
  name: "TUMSAT Etchujima Campus"
  approximate_position:
    latitude_deg: 35.6654
    longitude_deg: 139.7960
    height_m: 45.2
    coordinate_system: "WGS84"
observations:
  type: "dd"
  diff_interval_s: 1.0
  doppler_unit: "m/s"
  reference_frequency_hz: 11325000000
  time_system: "GPST"
  time_format: "gps_seconds"
  columns:
    - epoch
    - sat_id
    - norad_id
    - constellation
    - azimuth_deg
    - elevation_deg
    - value
    - sigma
    - cn0_dBHz
    - tone_index
    - quality_flag
receiver:
  sdr:
    type: "HackRF One"
    sampling_rate_hz: 2000000
    sample_bits: 8
    bandwidth_hz: 2000000
  antenna:
    type: "parabolic_dish+LNBF"
    dish_diameter_m: 0.45
    pointing:
      mode: "fixed"
      elevation_deg: 90.0
    lnb:
      type: "qro.cz SDR TCXO"
      lo_frequency_hz: 9750000000
      lo_stability: "tcxo"
      lo_stability_ppm: 2.0
gnss_reference:
  rinex_file: "TMS100JPN_R_20260740300_05M_MN.rnx"
  receiver_type: "Septentrio mosaic-X5"
  time_sync_method: "pps"
  time_sync_accuracy_s: 0.000001
orbit_source:
  type: "TLE"
  source: "space-track.org"
  propagator: "SGP4"
  tle_file: "starlink_20260315.tle"
processing:
  doppler_extraction:
    method: "fft_peak_tracking"
    fft_size: 65536
  satellite_identification:
    method: "sgp4_doppler_matching"
  lo_drift_correction:
    method: "epoch_differencing"
  azel_source:
    method: "sgp4_from_tle"
    reference: "orbit_source"
  quality_control:
    cn0_mask_dBHz: 15.0
    elevation_mask_deg: 10.0
comments:
  - "Clear sky, no interference detected"
%END_HEADER
%DATA
# epoch	sat_id	norad_id	constellation	azimuth_deg	elevation_deg	value	sigma	cn0_dBHz	tone_index	quality_flag
2247264001.000	STARLINK-1234	54321	STARLINK	180.3	78.2	-0.342	0.15	25.3	4	0
2247264002.000	STARLINK-1234	54321	STARLINK	180.5	78.0	-0.358	0.16	24.8	4	0
2247264003.000	STARLINK-1234	54321	STARLINK	180.8	77.7	-0.371	0.15	25.1	4	0
2247264003.000	STARLINK-5678	55432	STARLINK	045.1	62.3	+0.127	0.22	21.1	4	0
2247264004.000	STARLINK-1234	54321	STARLINK	181.0	77.4	-0.385	0.16	24.5	4	0
2247264004.000	STARLINK-5678	55432	STARLINK	045.6	62.0	+0.142	0.23	20.8	4	0
2247264005.000	STARLINK-1234	54321	STARLINK	181.3	77.1	-0.398	0.17	23.9	4	2
2247264005.000	STARLINK-5678	55432	STARLINK	046.0	61.7	+0.156	0.25	19.5	4	2
%END_DATA
```

---

## Appendix A: Design Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| YAML header over RINEX-style fixed-width | Flexible extensibility, self-describing | RINEX-style (hard to extend), JSON (no comments), TOML (verbose for deep nesting) |
| TSV data over CSV | Handles spaces in satellite names without quoting | CSV (requires quoting), fixed-width (column width management), binary (not human-readable) |
| NORAD ID as primary key | Permanently unique, direct TLE correspondence | Satellite name (subject to change), COSPAR ID (verbose), custom ID (non-standard) |
| GPS seconds for time | Maximum GNSS interoperability | ISO 8601 (parsing overhead), UNIX (leap second issues), MJD (non-GNSS convention) |
| Magic line MAJOR.MINOR only | Parser compatibility check needs only MAJOR.MINOR; PATCH is for errata. Matches RINEX convention | Full semver in magic line (verbose, mixes parser concerns with spec errata) |
| Satellite-focused v0.1 scope | Match author's research focus; avoid premature abstraction for terrestrial sources | Universal source model (over-engineered for current use cases) |
| Az/el as RECOMMENDED, not REQUIRED | Allow rare cases of raw-only recording without geometry computation | REQUIRED (excludes valid use cases), OPTIONAL (under-emphasizes importance) |
| Az/el provenance in header | Enable downstream software to decide whether to recompute from precise orbits | No provenance (users cannot assess accuracy), per-row provenance (excessive overhead) |
| NaN canonical form | Writers MUST emit `NaN`; parsers SHOULD accept common casings for interoperability. Matches pandas/numpy canonical representation while avoiding strict rejection of valid data | Fully case-insensitive (no canonical form), fully case-sensitive (rejects interoperable data) |
| `propagator` OPTIONAL for TLE | SGP4 is the only practical TLE propagator; requiring an explicit field adds boilerplate without information | REQUIRED (current practice universally uses SGP4; no real alternative) |
| Time-scale conversion out of scope | Parsers store epochs as-is; downstream software handles GPST↔UTC. Avoids embedding leap-second tables in a format parser | Parser handles conversion (complexity, maintenance burden, error-prone) |

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **SoOp** | Signals of Opportunity — exploiting signals not originally intended for positioning |
| **NORAD ID** | Satellite catalog number assigned by NORAD |
| **TLE** | Two-Line Element — orbital element set for SGP4 propagation |
| **LNB / LNBF** | Low Noise Block (Feed) — frequency converter/amplifier for satellite signal reception |
| **LO** | Local Oscillator — oscillator within LNB for frequency conversion |
| **IF** | Intermediate Frequency — frequency after LNB down-conversion |
| **PPP** | Precise Point Positioning |
| **PPP-RTK** | PPP with integer ambiguity resolution via network corrections |
| **TDCP** | Time-Differenced Carrier Phase |
| **C/N₀** | Carrier-to-noise density ratio (dB-Hz) |
| **ECEF** | Earth-Centered Earth-Fixed coordinate system |
| **CPI** | Coherent Processing Interval — integration time for spectral analysis |

---

## Appendix C: MIME Type and File Association

- File extension: `.soop`
- Compressed: `.soop.gz`
- Proposed MIME type: `application/vnd.soopex+yaml` (informational; not yet registered)

---

*SOOPEX Specification v0.1.0-draft — End of Document*
