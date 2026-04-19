"""SOOPEX file parser: .soop (or .soop.gz) → SoopObs."""

from __future__ import annotations

import gzip
import io
from pathlib import Path

import pandas as pd
from ruamel.yaml import YAML

from soopex.models import Header, SoopObs

_BOM = "\ufeff"
_GZIP_MAGIC = b"\x1f\x8b"

_INT_COLUMNS = frozenset({"norad_id", "tone_index", "quality_flag"})
_STRING_COLUMNS = frozenset({"sat_id", "constellation", "operator_sat_id"})


class SoopexFormatError(ValueError):
    """Raised when a file is not a well-formed SOOPEX file."""


def read(path: str | Path) -> SoopObs:
    """Parse a SOOPEX file and return a SoopObs.

    Args:
        path: Path to a .soop or .soop.gz file.

    Returns:
        SoopObs with typed header and a pandas DataFrame of observations.

    Raises:
        SoopexFormatError: File is missing required markers or is malformed.
        pydantic.ValidationError: Header fails schema validation.
    """
    text = _read_text(Path(path))
    lines = text.splitlines()
    if not lines:
        raise SoopexFormatError("empty file")

    _parse_magic(lines[0])

    header_dict = _extract_header(lines)
    header = Header.model_validate(header_dict)

    data_lines = _extract_data_lines(lines)
    df = _parse_data(data_lines, header.observations.columns)

    return SoopObs(header=header, data=df)


def _read_text(path: Path) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:2] == _GZIP_MAGIC:
        raw = gzip.decompress(raw)
    text = raw.decode("utf-8")
    if text.startswith(_BOM):
        text = text[len(_BOM) :]
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _parse_magic(line: str) -> str:
    parts = line.strip().split()
    if len(parts) < 2 or parts[0] != "%SOOPEX":
        raise SoopexFormatError(f"invalid magic line: {line!r}")
    return parts[1]


def _extract_header(lines: list[str]) -> dict:
    start = end = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "%HEADER" and start is None:
            start = i
        elif stripped == "%END_HEADER":
            end = i
            break
    if start is None:
        raise SoopexFormatError("missing %HEADER marker")
    if end is None:
        raise SoopexFormatError("missing %END_HEADER marker")

    yaml_text = "\n".join(lines[start + 1 : end])
    yaml = YAML(typ="safe")
    parsed = yaml.load(yaml_text)
    if not isinstance(parsed, dict):
        raise SoopexFormatError("header YAML did not parse to a mapping")
    return parsed


def _extract_data_lines(lines: list[str]) -> list[str]:
    start = end = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "%DATA" and start is None:
            start = i
        elif stripped == "%END_DATA":
            end = i
            break
    if start is None:
        raise SoopexFormatError("missing %DATA marker")
    if end is None:
        end = len(lines)

    out: list[str] = []
    for raw in lines[start + 1 : end]:
        if not raw.strip():
            continue
        if raw.lstrip().startswith("#"):
            continue
        out.append(raw)
    return out


def _parse_data(data_lines: list[str], columns: list[str]) -> pd.DataFrame:
    if not data_lines:
        return _empty_frame(columns)

    text = "\n".join(data_lines)
    df = pd.read_csv(
        io.StringIO(text),
        sep="\t",
        header=None,
        names=columns,
        dtype=str,
        keep_default_na=False,
        na_values=["NaN"],
    )
    return _coerce_dtypes(df, columns)


def _empty_frame(columns: list[str]) -> pd.DataFrame:
    series = {col: pd.Series(dtype=_column_dtype(col)) for col in columns}
    return pd.DataFrame(series, columns=columns)


def _coerce_dtypes(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in _STRING_COLUMNS:
            df[col] = df[col].astype("object")
        elif col in _INT_COLUMNS:
            numeric = pd.to_numeric(df[col], errors="coerce")
            if numeric.isna().any():
                df[col] = numeric.astype("Int64")
            else:
                df[col] = numeric.astype("int64")
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
    return df


def _column_dtype(name: str) -> str:
    if name in _STRING_COLUMNS:
        return "object"
    if name in _INT_COLUMNS:
        return "int64"
    return "float64"
