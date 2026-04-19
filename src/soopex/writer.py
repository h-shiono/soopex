"""SOOPEX file writer: SoopObs → .soop (or .soop.gz)."""

from __future__ import annotations

import gzip
import io
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd
from ruamel.yaml import YAML

from soopex._version import __version__

if TYPE_CHECKING:
    from soopex.models import SoopObs

MAGIC_VERSION = "0.1"
DEFAULT_GENERATOR = f"soopex {__version__}"

_THREE_DECIMAL_COLUMNS = frozenset({"epoch", "azimuth_deg", "elevation_deg"})
_INT_COLUMNS = frozenset({"norad_id", "tone_index", "quality_flag"})


def write(obs: SoopObs, path: str | Path, *, generator: str | None = None) -> None:
    """Serialize a SoopObs to ``path``.

    Paths ending in ``.gz`` are written gzip-compressed.
    """
    p = Path(path)
    text = _render(obs, generator=generator)
    raw = text.encode("utf-8")

    if p.suffix == ".gz":
        with gzip.open(p, "wb") as f:
            f.write(raw)
    else:
        with open(p, "wb") as f:
            f.write(raw)


def _render(obs: SoopObs, *, generator: str | None) -> str:
    buf = io.StringIO()
    buf.write(f"%SOOPEX {MAGIC_VERSION}\n")
    buf.write("%HEADER\n")
    _write_header_yaml(buf, obs, generator=generator)
    buf.write("%END_HEADER\n")
    buf.write("%DATA\n")
    _write_data_tsv(buf, obs)
    buf.write("%END_DATA\n")
    return buf.getvalue()


def _write_header_yaml(buf: io.StringIO, obs: SoopObs, *, generator: str | None) -> None:
    header_dict = obs.header.model_dump(exclude_none=True, by_alias=True)
    if generator is not None:
        header_dict.setdefault("format", {})["generator"] = generator
    header_dict = _strip_none(header_dict)

    yaml = YAML()
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.dump(header_dict, buf)


def _write_data_tsv(buf: io.StringIO, obs: SoopObs) -> None:
    columns = obs.header.observations.columns
    buf.write("# " + "\t".join(columns) + "\n")

    if obs.data.empty:
        return

    formatted = _format_frame(obs.data, columns)
    formatted.to_csv(
        buf,
        sep="\t",
        index=False,
        header=False,
        lineterminator="\n",
        na_rep="NaN",
    )


def _format_frame(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"DataFrame missing declared columns: {missing}")

    out = pd.DataFrame(index=df.index)
    for col in columns:
        series = df[col]
        if col in _THREE_DECIMAL_COLUMNS:
            out[col] = series.map(lambda v: "NaN" if pd.isna(v) else f"{float(v):.3f}")
        elif col in _INT_COLUMNS:
            out[col] = series.map(lambda v: "NaN" if pd.isna(v) else f"{int(v)}")
        elif pd.api.types.is_float_dtype(series):
            out[col] = series.map(lambda v: "NaN" if pd.isna(v) else _format_float(v))
        else:
            out[col] = series.map(lambda v: "" if pd.isna(v) else str(v))
    return out


def _format_float(v: float) -> str:
    formatted = f"{float(v):.6g}"
    if "." not in formatted and "e" not in formatted and "n" not in formatted:
        formatted += ".0"
    return formatted


def _strip_none(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_none(v) for v in obj]
    return obj
