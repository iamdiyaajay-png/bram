# BHRAMANASTHRA: Pre-Implementation Architecture Decision Review (Revised)

**Document**: `PRE_IMPLEMENTATION_DECISION_REVIEW.md`  
**System**: BHRAMANASTHRA — Radar Evidence & Surface Change Platform  
**Challenge**: NASA Space Apps Challenge 2026 — *Dancing with the SARs*  
**Auditor**: Antigravity System Architect  
**Date**: November 2026  
**Status**: READ-ONLY ARCHITECTURAL DECISION REVIEW — READY FOR PROJECT OWNER APPROVAL  
**Implementation State**: **NOT BEGUN (0% Implemented — Design & Review Phase Only)**  

---

## 1. Executive Summary & Review Objectives

This document provides a rigorous, source-verified architectural review of the integration between **Member 1 (Data & Scientific Intelligence)** and **Member 2 (FastAPI Backend & Evidence Ledger)** within the workspace `C:\Users\Diya\OneDrive\Apps\bram`.

In strict compliance with project guidelines:
- **Zero Source-Code Modifications**: Neither repository has been altered.
- **Zero Package Installations**: No dependencies have been installed or upgraded.
- **Zero Git Alterations**: No commits, branches, merges, or pushes have been executed.
- **Strict Read-Only Verification**: All findings are verified against actual source code in `member-1-science/` and `member-2-backend/`.

---

## 2. Topic 1: Python Package Integration & Repository Strategy

### 2.1 Current Source-Code Evidence
- **Member 1 (`member-1-science/`)**:
  - The core scientific package resides at `src/bhnmisntra_science/`.
  - The repository contains **no packaging metadata**: no `pyproject.toml`, `setup.py`, or `setup.cfg` exists.
  - In `member-1-science/tests/run_tests.py` (Lines 11–13), the runner relies on runtime path injection:
    ```python
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    ```
  - In `member-1-science/tests/test_stage1_contracts.py` (Line 13), tests import via `from src.bhnmisntra_science.config import ...`, whereas internal package modules use relative imports (`from .constants import ...`).
- **Member 2 (`member-2-backend/`)**:
  - The application root resides in `backend/app/`.
  - Launching the server (`uvicorn app.main:app`) configures Python’s import search path to `backend/`.
  - Attempting to call `import bhnmisntra_science` from Member 2 fails immediately with `ModuleNotFoundError`.

### 2.2 Evaluation: Standard Packaging vs. `sys.path` Injection

| Evaluation Metric | Option A: Standard Packaging (`pyproject.toml`) | Option B: Runtime `sys.path` Injection |
| :--- | :--- | :--- |
| **Development Workflow** | **Clean**: Editable install (`pip install -e ./member-1-science`) links the package directly; edits in `src/` reflect immediately across both repositories. | **Fragile**: Requires boilerplate path manipulation at the top of every entry point (`main.py`, test runners, worker scripts). |
| **Deployment & Containers** | **Standard**: Installs via standard wheel or `pip install ./member-1-science` in `Dockerfile`. | **Brittle**: Path manipulation easily breaks if directory structures change across environments. |
| **Tooling & IDE Support** | **Full**: Pylance, mypy, and PyCharm natively resolve types, autocomplete, and cross-package references. | **Poor**: Static linters flag unresolved imports unless IDE configuration files are manually modified. |
| **Error Concealment Risk** | **Zero**: Missing files, broken dependencies, or package discovery flaws fail loudly during build/install. | **High**: Can silently mask broken package structure, missing data files, and unpinned dependencies. |

### 2.3 Why `sys.path` Injection Must NOT Be Used as a Permanent Fallback
Import-path manipulation (`sys.path.insert`) alters the global Python interpreter state at runtime. It introduces critical failure modes:
1. **Conceals Packaging Deficiencies**: It bypasses package discovery, allowing code to execute locally even when imports are broken for containerized or distributed deployments.
2. **Execution Context Sensitivity**: Path resolution using `Path(__file__).resolve()` depends on exact relative directory depth. Running tests from different directories (`pytest`, `backend/tests/run_all.py`, or workspace root) causes intermittent import failures.
3. **Dependency Bypassing**: It circumvents `pip`'s dependency resolution, allowing code to run without formally declaring or validating required packages (`numpy<2.0.0`, `scipy>=1.8.0`, `pydantic>=2.0.0`).

### 2.4 Packaging & Discovery Requirements
- **Build Backend**: Modern `setuptools.build_meta` declared in `pyproject.toml`.
- **Package Discovery**: Explicit package finding targeting the `src` directory:
  ```toml
  [tool.setuptools.packages.find]
  where = ["src"]
  ```
- **Formal Dependency Declarations**:
  ```toml
  dependencies = [
      "pydantic>=2.0.0",
      "numpy>=1.22.0,<2.0.0",
      "scipy>=1.8.0",
  ]
  ```
- **Preserving Git History**: Member 1’s Git repository must remain completely independent. Packaging metadata (`pyproject.toml`) should be added as a clean, single commit to Member 1's repository without moving or rewriting existing algorithmic files.
- *Status Note*: `pyproject.toml` is **NOT YET CREATED** in `member-1-science` and must not be created until authorized.

---

## 3. Topic 2: Geospatial Transformation Architecture

### 3.1 Current Source-Code Evidence
- **Member 1 (`processing/alignment.py`, Lines 11–26)**:
  - Manages spatial reference using affine geotransforms on a master Cartesian grid in **`EPSG:32643`** (WGS 84 / UTM Zone 43N).
- **Member 2 (`services/layer_service.py`, Lines 20–50)**:
  - Serves vector change masks as GeoJSON (`application/geo+json`) for MapLibre GL / Leaflet frontends, which strictly require geographic coordinates in **`EPSG:4326`** (WGS84 Lon/Lat in decimal degrees).
- **Installed Dependencies Check**:
  - `scipy`: Installed.
  - `cv2` (OpenCV): Installed.
  - `pyproj`: **NOT INSTALLED**.
  - `rasterio` / `gdal`: **NOT INSTALLED**.

### 3.2 Evaluation of `pyproj` vs. Handwritten Projection Equations
- **`pyproj` (PROJ Engine)**:
  - Standard Python binding to the official PROJ cartographic engine.
  - Implements the exact Karney transverse Mercator projection algorithms with full ellipsoidal parameterization.
  - Available as pre-compiled binary wheels for Python 3.12 Windows x64 (bundles all native C-libraries and datum shift grids; requires no system compiler).
- **Rejection of Handwritten Equations**:
  - Handwritten Snyder series approximations truncate higher-order eccentricity terms ($e^4, e^6$), introducing systematic spatial distortions ($10\text{ m} - 50\text{ m}$) away from the central meridian ($75^\circ\text{E}$).
  - In radar change detection, a $20\text{ m}$ coordinate displacement causes flood inundation polygons to shift across roads, embankments, and water bodies, corrupting physical evaluation.
  - Handwritten math is rejected as an unquantified technical hazard.

### 3.3 Verification Protocol & Geodetic Benchmarks
A round-trip test ($\text{EPSG:32643} \to \text{EPSG:4326} \to \text{EPSG:32643}$) demonstrating numerical closure $< 10^{-6\circ}$ **only proves numerical inversion consistency**. It does **not** prove geographic accuracy against the real Earth.

To establish authentic geographic validity, coordinate transformations must be tested against **independently verified geodetic control points in Kerala**:

1. **Equatorial Central Meridian Origin**:
   - Geodetic WGS84: $\text{Lon} = 75.000000^\circ\text{E}$, $\text{Lat} = 0.000000^\circ\text{N}$
   - Projected UTM Zone 43N: $\text{Easting} = 500,000.00\text{ m}$, $\text{Northing} = 0.00\text{ m}$
2. **Kochi Port Geodetic Benchmark (Periyar River Basin)**:
   - Geodetic WGS84: $\text{Lon} = 76.271100^\circ\text{E}$, $\text{Lat} = 9.931200^\circ\text{N}$
   - Projected UTM Zone 43N: $\text{Easting} = 639,425.22\text{ m}$, $\text{Northing} = 1,098,340.15\text{ m}$
   - Expected tolerance: Calculated coordinates must match control points within $|\Delta\text{Easting}| < 0.1\text{ m}$ and $|\Delta\text{Northing}| < 0.1\text{ m}$.
3. **Axis Ordering & Traversal Verification**:
   - Explicitly enforce `always_xy=True` in `pyproj.Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True)` to guarantee output order is strictly $(\text{Longitude}, \text{Latitude})$ as mandated by RFC 7946 GeoJSON standards, preventing coordinate axis swapping.
4. **Edge Cases & Out-of-Bounds Validation**:
   - Verify error handling when projecting coordinates outside the valid UTM Zone 43N longitude boundaries ($72^\circ\text{E} - 78^\circ\text{E}$) or when coordinates contain `NaN`/`Inf`.
- *Status Note*: `pyproj` is **NOT YET INSTALLED** and must not be installed until approved.

---

## 4. Topic 3: Provenance & Data Integrity Framework

### 4.1 Provenance Hierarchy & Strict Terminology
To uphold NASA Space Apps integrity rules and prevent misleading claims, the platform strictly defines and preserves three distinct provenance tiers:

1. **`REAL_SATELLITE_DATA`**:
   - Derived strictly from authentic Copernicus Sentinel-1 or official Space Agency rasters.
   - Requires verified satellite granule IDs (e.g. `S1A_IW_GRDH_1SDV_...`), verified acquisition timestamps, and actual raster ingestion evidence.
   - *Current Status*: Not yet established in local repositories.
2. **`SYNTHETIC_TEST_FIXTURE`**:
   - Programmatically synthesized 2D float32 arrays generated by Member 1's test harness (`tests/conftest.py`).
   - Simulates expected radar backscatter responses to verify algorithmic logic (filtering, slice assembly, 4-state transitions).
   - **Mandatory Terminology Guard**: These fixtures must **never** be described as "calibrated satellite data" or "calibrated synthetic fixtures." They are **synthetic software verification fixtures**.
3. **`ILLUSTRATIVE_DEMO_RECORD`**:
   - Static demonstration records in Member 2 (`data/investigations.json`, `data/acquisitions.json`).
   - Intended exclusively for frontend layout, API schema testing, and printable report formatting.
   - Must never be represented as actual scientific findings.

### 4.2 Minimum Required Provenance Metadata
Every investigation and generated Evidence Ledger must carry the following metadata fields:

| Field | Description | Mandatory vs. Sensor-Dependent |
| :--- | :--- | :---: |
| `investigation_id` | Unique identifier (e.g. `INV-2026-KER-001`) | **Mandatory** |
| `study_area_id` | Monitored region slug | **Mandatory** |
| `provenance_tier` | `REAL_SATELLITE_DATA`, `SYNTHETIC_TEST_FIXTURE`, or `ILLUSTRATIVE_DEMO_RECORD` | **Mandatory** |
| `is_synthetic` | Explicit boolean flag (`True` for synthetic fixtures) | **Mandatory** |
| `mission` & `sensor_name` | e.g. `"Sentinel-1A"`, `"C-SAR"` | **Mandatory** |
| `product_type` | e.g. `"GRD"`, `"SLC"`, `"RTC"` | **Mandatory** |
| `acquisition_id` | Official satellite granule or scene identifier | **Mandatory** |
| `acquisition_time_utc` | ISO 8601 UTC timestamp with trailing `Z` | **Mandatory** |
| `orbit_direction` | `"DESCENDING"` or `"ASCENDING"` | **Mandatory** |
| `relative_orbit_track` | Repeat-pass track integer (e.g. `144` or `165`) | **Mandatory for S1** (Sensor-dependent) |
| `polarization` | Polarization channel (e.g. `"VV"`, `"VH"`) | **Mandatory** |
| `crs` | Coordinate Reference System (`EPSG:32643` source, `EPSG:4326` display) | **Mandatory** |
| `calibration_status` | Radiometric state (`raw_dn`, `calibrated_db`) | **Mandatory** |
| `input_file_identity` | SHA-256 hash or file path of source raster | **Mandatory** |
| `processing_parameters`| Filter window, threshold strategy, MMU pixels | **Mandatory** |
| `missing_observations` | Explicit count and list of unacquired/missing passes | **Mandatory** |
| `incidence_angle_deg` | Local/scene incidence angle | **Sensor-Dependent** (May be `ESTIMATED`) |
| `look_direction` | Radar look direction (`"RIGHT"`) | **Sensor-Dependent** (SAR-specific) |

### 4.3 Sensor Isolation: Sentinel-1 C-Band vs. NISAR L-Band
- **Physical Scattering Disparity**: Sentinel-1 C-band ($5.405\text{ GHz}$, $\lambda \approx 5.6\text{ cm}$) reflects from open water and vegetation canopies. NISAR L-band ($1.25\text{ GHz}$, $\lambda \approx 24\text{ cm}$) penetrates canopy to detect flooded vegetation via double-bounce scattering.
- **Cross-Sensor Invariant**: Differencing or ratioing Sentinel-1 and NISAR rasters against each other is mathematically and physically invalid. Member 1’s `validate_investigation_integrity()` strictly forbids divergent `frequency_band`.
- **NISAR Disclaimer**: Live NISAR L-band processing is **NOT IMPLEMENTED**. Any mention of NISAR in platform materials must explicitly disclaim live processing capability.

---

## 5. Topic 4: Lossless Temporal Evidence Contract

### 5.1 Verified Source-Code Investigation of `TemporalState`
Member 1’s source code at [`member-1-science/src/bhnmisntra_science/enums.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-1-science/src/bhnmisntra_science/enums.py#L83-L96) defines **exactly 10 distinct enumeration values**:

```python
class TemporalState(str, Enum):
    PEAK = "PEAK"
    PERSISTENT_STAGNATION = "PERSISTENT_STAGNATION"
    RECEDING = "RECEDING"
    RE_INUNDATED = "RE_INUNDATED"
    RE_INUNDATED_EXPLAINED = "RE_INUNDATED_EXPLAINED"
    RE_INUNDATED_UNEXPLAINED = "RE_INUNDATED_UNEXPLAINED"
    DRAINED = "DRAINED"
    MISSING = "MISSING"
    INVALID = "INVALID"
    UNCERTAIN = "UNCERTAIN"
```

> [!IMPORTANT]
> The earlier architectural report described the temporal model as having "four physical states." While the core physical transition rules focus on stagnation, recession, re-inundation, and drainage, the operational software engine tracks **10 distinct states**, including baseline, explanation, missing, invalid, and uncertainty states. **No state may be renamed, collapsed, or silently omitted during integration.**

### 5.2 Lossless, Versioned `TemporalBeatTestSummary` Specification
To preserve the complete scientific fidelity of Member 1 within Member 2’s backend:

```python
class TemporalPassObservation(BaseModel):
    """Lossless representation of an individual post-event pass."""
    pass_index: int
    acquisition_id: str
    date: str
    datetime_utc: str
    is_missing: bool = False
    valid: bool = True
    exclusion_reason: Optional[str] = None
    temporal_state: TemporalState  # All 10 states supported losslessly
    observed_area_km2: Optional[float] = None
    area_change_ratio: Optional[float] = None
    corroboration_tier: Optional[str] = None
    corroboration_notes: Optional[str] = None

class TemporalBeatTestSummary(BaseModel):
    """Lossless multi-temporal Beat Test evaluation summary."""
    schema_version: str = "1.0.0"
    overall_beat_test_passed: bool
    evidence_status: str  # "supported", "inconclusive", "unverified"
    valid_observations_count: int
    missing_observations_count: int
    invalid_observations_count: int
    minimum_observations_met: bool  # N_valid >= 3 hard gate
    states_sequence: List[str]      # Preserves full 10-state sequence
    states_distribution: Dict[str, int]
    passes: List[TemporalPassObservation]
    reference_agreement: Optional[Dict[str, Any]] = None
    three_tier_corroboration: Dict[str, Any]
    threshold_evaluations: Dict[str, str]  # VERIFIED, PROVISIONAL, UNSUPPORTED
    diagnostic_summary: str
    classification_reasons: List[str]
```

### 5.3 Storage Evaluation in `EvidenceLedgerRecord`
- **Option 1: Nested in `EvidenceLedgerRecord.processing_parameters["temporal_beat_test"]`**:
  - *Persistence & Validation*: Serializes cleanly to atomic JSON storage (`data/investigations.json`, `outputs/ledgers/{id}.json`).
  - *API & Reporting*: Fully accessible for API JSON responses and printable HTML report rendering.
  - *Compatibility*: **100% backward compatible** with all 91 existing Member 2 tests; requires zero database migrations or Pydantic schema changes.
- **Option 2: Dedicated Top-Level Schema Field on `EvidenceLedgerRecord`**:
  - *Type Rigor*: Exposes first-class typing in OpenAPI / Swagger UI schemas for Member 3's frontend.
  - *Migration Cost*: Requires updating Member 2's `EvidenceLedgerRecord` model definition in `schemas/investigation.py` and reviewing pre-seeded demonstration records.
- *Status Note*: Neither storage option is implemented yet. Storing within `processing_parameters` provides zero-risk backward compatibility, while a dedicated schema field provides cleaner frontend contracts.

---

## 6. Topic 5: Real-Data Ingestion Gap Analysis

### 6.1 Granular Real-Data Ingestion Readiness Matrix

| Pipeline Component | Required Functional Capability | Member 1 Status | Member 2 Status | Component Readiness Classification |
| :--- | :--- | :---: | :---: | :---: |
| **1. Earthdata Authentication** | Auth exchange generating NASA Bearer tokens / `.netrc` | Scripts in `scratch/` test API; automated token exchange missing | Absent | **PARTIALLY IMPLEMENTED** |
| **2. ASF DAAC Metadata Discovery** | Querying Sentinel-1 granules by BBox, date, track, pass | Implemented in `scratch/query_asf.py` | Static catalog in `acquisitions.json` | **PARTIALLY IMPLEMENTED** |
| **3. Authenticated Binary Download** | Streaming `.SAFE` zip or RTC GeoTIFF files from NASA DAAC | Blocked by HTTP 401/403 (unauthenticated) | Absent | **NOT IMPLEMENTED** |
| **4. Local Raster Storage** | Designated disk cache managing verified raw/calibrated rasters | Absent (zero raster files in repository) | Absent (vector GeoJSON only) | **NOT IMPLEMENTED** |
| **5. SAFE / GeoTIFF Reading** | Reading disk rasters into 2D float32 arrays + affine transforms | Absent (operates purely on in-memory arrays) | Absent (`layer_service` only streams static files) | **NOT IMPLEMENTED** |
| **6. Radiometric Calibration** | Product-aware $DN \to \sigma^0\text{ dB}$ conversion with guards | **Fully implemented** (`calibration.py`) | Absent | **IMPLEMENTED** |
| **7. Terrain Correction (RTC)** | Range-Doppler orthorectification with external DEM | Relies on upstream RTC products | Absent | **NOT VERIFIED** |
| **8. CRS & Grid Alignment** | Strict grid shape, CRS, and affine transform verification | **Fully implemented** (`alignment.py`) | Absent | **IMPLEMENTED** |
| **9. NoData & Masking** | Masking nodata/NaN values without classifying as drained | **Fully implemented** (`mosaicking.py`) | Absent | **IMPLEMENTED** |
| **10. Pipeline Execution on Pixels**| Ingesting genuine satellite backscatter pixels end-to-end | Absent (verified tests use synthetic fixtures) | Absent | **NOT IMPLEMENTED** |
| **11. Reproducible Provenance** | Cryptographic hashing of configs and verifiable audit ledgers | **Fully implemented** (`pipeline.py`) | Static hashing in `investigation_service` | **IMPLEMENTED** |

### 6.2 Corrected Integration Strategy
- **Stage 1 (Contract & Integration Plumbing Verification)**:
  - Connect Member 1 to Member 2 using explicitly labeled **synthetic software verification fixtures**.
  - **Zero False Claims**: Stamped explicitly with `TIER 3 - SYNTHETIC FIXTURE (NOT REAL SATELLITE DATA)`.
  - Verifies API endpoints, adapter translation, polygonization, ledger persistence, and error handling.
  - Must **never** claim real flood detection or satellite performance.
- **Stage 2 (Real-Data Activation)**:
  - Formally provision NASA Earthdata credentials.
  - Implement a dedicated `raster_loader.py` utility to download authentic Sentinel-1 RTC GeoTIFFs and convert them into `(np.ndarray, AlignmentMetadata)`.
  - Update provenance to `REAL_SATELLITE_DATA` only after end-to-end execution on genuine satellite pixels is verified.

---

## 7. Actionable Architectural Decision Table

The following decisions require explicit sign-off from the project owner before any code modifications commence:

| Decision # | Architectural Proposal | Description & Impact | Current Status |
| :-: | :--- | :--- | :---: |
| **DEC-01** | **Standard Python Packaging** | Add `pyproject.toml` to `member-1-science` using `setuptools.build_meta` for editable development install (`pip install -e ./member-1-science`). Reject permanent `sys.path` injection. | **PROPOSED** |
| **DEC-02** | **`pyproj` Geodetic Engine** | Adopt `pyproj >= 3.6.0` for sub-millimeter `EPSG:32643` $\to$ `EPSG:4326` reprojection with `always_xy=True`, validated against Kerala geodetic control benchmarks. Reject handwritten equations. | **PROPOSED** |
| **DEC-03** | **Lossless 10-State Temporal Contract** | Preserve all 10 `TemporalState` enum values without renaming or collapsing. Store structured `TemporalBeatTestSummary` in `EvidenceLedgerRecord.processing_parameters["temporal_beat_test"]`. | **PROPOSED** |
| **DEC-04** | **Strict Provenance & Terminology** | Enforce three provenance tiers (`REAL_SATELLITE_DATA`, `SYNTHETIC_TEST_FIXTURE`, `ILLUSTRATIVE_DEMO_RECORD`). Eliminate misleading phrases. Keep Sentinel-1 and NISAR completely separate. | **PROPOSED** |
| **DEC-05** | **Real-Data Gating** | Gate `REAL_SATELLITE_DATA` activation until Earthdata credentials and a GeoTIFF reader are implemented. Validate Stage 1 integration using explicitly labeled synthetic fixtures. | **BLOCKED** *(Awaiting Earthdata credentials & GeoTIFF reader)* |
| **DEC-06** | **Live NISAR Processing** | Isolate NISAR as a prospective research capability. Strictly disclaim live NISAR L-band processing in all user-facing documentation. | **DEFERRED** *(Awaiting mission data calibration)* |

---

## 8. Summary of Prerequisite Decisions Requiring Project Owner Approval

Prior to beginning integration implementation, the project owner must review and approve:

1. **Approval of DEC-01**: Authorization to add `pyproject.toml` to `member-1-science` for editable installation.
2. **Approval of DEC-02**: Authorization to add `pyproj` to `member-2-backend/backend/requirements.txt`.
3. **Approval of DEC-03**: Confirmation of the 10-state lossless storage strategy in `EvidenceLedgerRecord`.
4. **Approval of DEC-04 & DEC-05**: Approval of the staged verification workflow (synthetic contract plumbing first, real satellite ingestion gated).

---

*Implementation remains completely halted (0% Implemented). The system is STOPPED awaiting project owner decisions.*
