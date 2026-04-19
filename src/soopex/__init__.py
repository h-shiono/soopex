"""SOOPEX: Signals of Opportunity Observation Exchange Format.

Reader, writer, and validator for the SOOPEX (.soop) file format.
"""

from soopex._version import __version__
from soopex.models import (
    LNB,
    SDR,
    Antenna,
    AntennaPointing,
    ApproximatePosition,
    AzelSource,
    FormatInfo,
    GnssReference,
    Header,
    Observations,
    OrbitSource,
    Processing,
    Receiver,
    Session,
    Simulation,
    Site,
    SoopObs,
)
from soopex.reader import SoopexFormatError, read
from soopex.validator import ValidationResult, validate
from soopex.writer import write

__all__ = [
    "LNB",
    "SDR",
    "Antenna",
    "AntennaPointing",
    "ApproximatePosition",
    "AzelSource",
    "FormatInfo",
    "GnssReference",
    "Header",
    "Observations",
    "OrbitSource",
    "Processing",
    "Receiver",
    "Session",
    "Simulation",
    "Site",
    "SoopObs",
    "SoopexFormatError",
    "ValidationResult",
    "__version__",
    "read",
    "validate",
    "write",
]
