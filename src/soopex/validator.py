"""SOOPEX file validation: schema + semantic checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from soopex.models import SoopObs
from soopex.reader import SoopexFormatError, read


@dataclass
class ValidationResult:
    """Result of validating a SOOPEX file."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate(path: str | Path) -> ValidationResult:
    """Validate a SOOPEX file against the v0.1 specification.

    Performs two-level validation:
    1. Schema: file structure and header fields via Pydantic.
    2. Semantic: column consistency, NORAD ID positivity, az/el ranges,
       per-satellite epoch monotonicity.
    """
    errors: list[str] = []
    warnings: list[str] = []

    try:
        obs = read(path)
    except SoopexFormatError as exc:
        errors.append(f"format: {exc}")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
    except ValidationError as exc:
        for err in exc.errors():
            loc = ".".join(str(x) for x in err["loc"])
            errors.append(f"schema: {loc}: {err['msg']}")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
    except (pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        errors.append(f"data: {exc}")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
    except (UnicodeDecodeError, OSError) as exc:
        errors.append(f"io: {exc}")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    _check_semantics(obs, errors, warnings)
    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)


def _check_semantics(obs: SoopObs, errors: list[str], warnings: list[str]) -> None:
    df = obs.data
    declared = obs.header.observations.columns
    if list(df.columns) != list(declared):
        errors.append(
            f"data: columns {list(df.columns)} do not match "
            f"header.observations.columns {list(declared)}"
        )
        return

    if df.empty:
        return

    if "norad_id" in df.columns:
        numeric = pd.to_numeric(df["norad_id"], errors="coerce")
        if numeric.isna().any():
            errors.append("data: norad_id column contains non-integer values")
        else:
            bad = numeric[numeric <= 0]
            if not bad.empty:
                errors.append(
                    f"data: norad_id must be positive integers; "
                    f"found {int(bad.min())} and {len(bad)} other(s)"
                )

    if "azimuth_deg" in df.columns:
        az = pd.to_numeric(df["azimuth_deg"], errors="coerce")
        bad = az[(az < 0) | (az >= 360)].dropna()
        if not bad.empty:
            errors.append(f"data: azimuth_deg out of range [0, 360); {len(bad)} row(s)")

    if "elevation_deg" in df.columns:
        el = pd.to_numeric(df["elevation_deg"], errors="coerce")
        bad = el[(el < 0) | (el > 90)].dropna()
        if not bad.empty:
            errors.append(f"data: elevation_deg out of range [0, 90]; {len(bad)} row(s)")

    if "epoch" in df.columns and "norad_id" in df.columns:
        for sat_id, group in df.groupby("norad_id", sort=False):
            epochs = pd.to_numeric(group["epoch"], errors="coerce")
            if epochs.diff().lt(0).any():
                errors.append(
                    f"data: epoch not monotonically non-decreasing for norad_id={int(sat_id)}"
                )

    if "cn0_dBHz" in df.columns:
        cn0 = pd.to_numeric(df["cn0_dBHz"], errors="coerce").dropna()
        if not cn0.empty and (cn0 < 0).any():
            warnings.append("data: some cn0_dBHz values are negative")
