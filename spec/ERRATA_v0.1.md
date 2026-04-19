# SOOPEX v0.1 — Errata & Open Questions

This document captures ambiguities, open questions, and suggested
clarifications discovered while building the reference implementation
(`soopex` 0.1.0a1). Each item is either (a) a deviation the implementation
makes from the spec's literal wording, (b) a place where the spec is silent
and the implementation makes a choice, or (c) a question the spec author
should resolve before v0.1 is finalized.

Nothing here is authoritative until folded back into `SOOPEX_SPEC_v0.1.md`.

---

## §3 File Structure

### 3.1 BOM handling (spec silent → implementation strips)

The spec does not mention UTF-8 BOMs. The reference implementation strips a
leading `U+FEFF` if present, before magic-line parsing.

**Proposal:** Add to §3: *"A UTF-8 BOM, if present at the start of the
file, MUST be ignored by parsers."*

### 3.2 CRLF normalization is one-way (spec silent → implementation normalizes on read only)

Spec §3 says LF is RECOMMENDED and CRLF is permitted but does not specify
parser behavior. The reference implementation normalizes CRLF → LF on
read. On write, it always emits LF.

**Proposal:** Explicitly document that parsers MUST accept CRLF by
normalizing to LF, and writers SHOULD emit LF.

### 3.3 Content after `%END_DATA` (spec silent → implementation ignores)

Spec does not say whether lines after `%END_DATA` are permitted. The
reference implementation reads up to `%END_DATA` and silently ignores
trailing content.

**Proposal:** Pick one of: (a) forbid trailing content (strict), (b) allow
only whitespace / comment lines (moderate), or (c) explicitly allow arbitrary
trailing content as long as `%END_DATA` is present (lenient — the current
implementation).

---

## §4 Header

### 4.1 `orbit_source.propagator` default for TLE (spec says REQUIRED, implementation enforces)

§4.2.5 declares `propagator` as "REQUIRED if type=TLE" but lists `"SGP4"` as
the only practical value. Since virtually every TLE user wants SGP4, the
spec could either (a) make `propagator` OPTIONAL with default `"SGP4"`, or
(b) keep the current REQUIRED behavior. The reference implementation keeps
it REQUIRED.

**Question:** Is there a case where a non-SGP4 propagator is used with TLE?
If not, default to `"SGP4"`.

### 4.2 Conditional required-field semantics

§4.2.4 uses the phrase "REQUIRED if type=dd" and similar. The reference
implementation enforces these via Pydantic model validators. The spec would
benefit from a crisper statement that these conditions are validation
errors, not merely strong recommendations.

### 4.3 `extra` fields (spec §7 "forward compatibility" not fully aligned with §9 `extensions`)

Spec §7 says parsers "MUST ignore unknown optional fields." §9 proposes an
`extensions:` block for future use. The reference implementation treats
these consistently: unknown fields at any depth are accepted (via Pydantic
`extra="allow"`), and the `extensions` block is accepted as a free-form
dict.

**Proposal:** Clarify in §9 that `extensions` is a convention for opt-in
experimental features, while §7's forward-compatibility rule applies to all
unknown optional keys regardless of whether they appear under `extensions`.

---

## §5 Data Block

### 5.1 Integer column NaN representation (spec §5.4 says "promote to float64" — implementation uses pandas Int64 nullable)

Spec §5.4 says: *"Integer columns with missing values SHOULD use `-1` as a
sentinel where semantically unambiguous, or be promoted to float64 and use
NaN."*

The reference implementation reads integer columns as `int64` when no NaN
is present, and as pandas nullable `Int64` when NaN is present — **not**
promoted to `float64`. This preserves integer semantics (e.g., `norad_id`
remains integer-typed) and is pandas-idiomatic but deviates from the spec.

**Proposal:** Update §5.4 to allow nullable-integer representation in
addition to float64 promotion.

### 5.2 `epoch` sort order (spec says SHOULD, not MUST — implementation does not resort)

§5.1 states: *"Data rows SHOULD be sorted by `epoch` in ascending order."*
The reference validator checks per-satellite monotonicity but does not
enforce global ascending order on read, and does not resort on write.

**Proposal:** Keep as SHOULD but consider adding a writer option to
optionally enforce sort on output.

### 5.3 `NaN` case sensitivity and whitespace

Spec §5.1 mandates case-sensitive `NaN`. The reference implementation
passes this through `pd.read_csv(... na_values=["NaN"])`. A bare field of
`"nan"` or `"NAN"` will be read as the literal string, which for a numeric
column coerces to `NaN` anyway via `pd.to_numeric(errors="coerce")` — so
the strictness is not fully enforced end-to-end.

**Proposal:** Either (a) strictly reject non-`NaN` casings, or (b) soften
the spec to allow any common casing. The reference implementation is
lenient by accident; the spec should pick a side.

### 5.4 Multi-epoch empty lines (spec silent → implementation skips blank lines)

Spec §5.1 does not say whether blank lines inside the data block are
errors. The reference implementation silently skips them.

**Proposal:** Document that blank lines in the data block MUST be ignored
by parsers.

---

## §6 Time Systems

### 6.1 GPST ↔ UTC leap-second handling (spec §6.2 is a pointer, not a procedure)

§6.2 says parsers "MUST handle the GPS–UTC offset correctly." The reference
implementation does not perform any conversions (it stores epochs as-is
per the declared `time_format`). Any conversion is left to the consumer.

**Proposal:** Rephrase §6.2 to: *"Parsers MUST preserve the declared
`time_system` and `time_format`; time-scale conversions are out of scope
for this specification."*

---

## Table of proposed changes for v0.1 final

| Section | Issue | Proposed action |
|---------|-------|-----------------|
| §3 | BOM handling | Add "MUST be stripped on read" |
| §3 | CRLF handling | Add "parsers MUST accept; writers SHOULD emit LF" |
| §3 | Post-`%END_DATA` content | Decide on strictness |
| §4.2.5 | `propagator` for TLE | Consider OPTIONAL with default `"SGP4"` |
| §5.4 | Nullable integers | Allow alongside float64 promotion |
| §5.1 | Blank lines in data | Document as ignored |
| §6.2 | Leap-second conversion | Clarify scope |

---

*SOOPEX Errata v0.1 — compiled during reference implementation
(soopex 0.1.0a1), 2026-04-19*
