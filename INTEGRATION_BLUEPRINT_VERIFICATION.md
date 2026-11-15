# BHRAMANASTHRA: Integration Architecture Blueprint Verification Report

**Audit Date**: November 15, 2026  
**Auditor**: Antigravity System Architect & Verification Agent  
**Audited Document**: `INTEGRATION_ARCHITECTURE_BLUEPRINT.md`  
**Referenced Codebases**:
- `member-1-science/` (Commit `79c0596`, Branch `main`)
- `member-2-backend/` (Commit `6751ab7`, Branch `main`)  
**Audit Scope**: Line-by-line verification of architectural assertions against verified source code and installed environment dependencies.  
**Classification Categories**: `VERIFIED`, `VERIFIED WITH CONDITIONS`, `NOT IMPLEMENTED`, `INCORRECT`.  

---

## 1. Executive Summary of Verification Results

| # | Verification Focus | Classification | Exact Source File Reference |
| :-: | :--- | :---: | :--- |
| **1** | Exact `run_scientific_pipeline()` function signature | **VERIFIED** | `member-1-science/src/bhnmisntra_science/pipeline.py` (Lines 214–225) |
| **2** | Exact `InvestigationConfig` constructor requirements | **VERIFIED** | `member-1-science/src/bhnmisntra_science/config.py` (Lines 432–488) |
| **3** | Exact `SlicePair` and raster input structures | **VERIFIED** | `member-1-science/src/bhnmisntra_science/processing/mosaicking.py` (Lines 56–65) & `pipeline.py` (Lines 80–135) |
| **4** | Exact `PipelineExecutionResult` fields and types | **VERIFIED** | `member-1-science/src/bhnmisntra_science/pipeline.py` (Lines 60–78) |
| **5** | `allow_missing_subsequent` supported argument | **VERIFIED** | `member-1-science/src/bhnmisntra_science/pipeline.py` (Lines 220, 241, 269, 396) |
| **6** | Adapter input construction from backend data | **VERIFIED WITH CONDITIONS** | `member-2-backend/backend/data/acquisitions.json` & `study_areas.json` |
| **7** | Existence of genuine raster loading code | **NOT IMPLEMENTED** | `member-1-science/src/` & `member-2-backend/backend/app/` |
| **8** | Raster vectorization & reprojection via dependencies | **VERIFIED WITH CONDITIONS** | Active Python Environment Check (`scipy`, `cv2` vs `pyproj`, `rasterio`) |
| **9** | `EvidenceLedgerRecord` metric preservation | **VERIFIED WITH CONDITIONS** | `member-2-backend/backend/app/schemas/investigation.py` (Lines 45–89) |
| **10**| Submodule structure reliable Python imports | **VERIFIED WITH CONDITIONS** | `member-1-science/` root inspection (`sys.path` injection required) |
| **11**| `POST /api/investigations/{id}/run` endpoint fit | **VERIFIED** | `member-2-backend/backend/app/routes/investigations.py` (Lines 25–48) |
| **12**| Temporal sequence example data authenticity | **VERIFIED WITH CONDITIONS** | `member-1-science/tests/test_four_state_tracker.py` & `member-2-backend/backend/data/` |

---

## 2. Detailed Technical Point-by-Point Verification

### Point 1: Exact `run_scientific_pipeline()` Function Signature
- **Classification**: **VERIFIED**
- **Source Reference**: [`member-1-science/src/bhnmisntra_science/pipeline.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-1-science/src/bhnmisntra_science/pipeline.py#L214-L225)
- **Verified Code Implementation**:
  ```python
  def run_scientific_pipeline(
      config: InvestigationConfig,
      raster_data: Mapping[str, Any] | None = None,
      slice_data: Mapping[str, Any] | None = None,
      environmental_context: Sequence[dict[str, Any] | None] | None = None,
      master_grid: AlignmentMetadata | None = None,
      data_authenticity_tier: str = "TIER 3 - SYNTHETIC FIXTURE (NOT REAL SATELLITE DATA)",
      allow_missing_subsequent: bool = False,
      allow_partial_slices: bool = False,
      reference_evidence: dict[str, Any] | None = None,
  ) -> PipelineExecutionResult:
  ```
- **Finding**: The signature stated in `INTEGRATION_ARCHITECTURE_BLUEPRINT.md` Section 3.2 matches the actual source code with 100% parameter-for-parameter precision. All 9 parameters, their types, and default values are identical.

---

### Point 2: Exact `InvestigationConfig` Constructor Requirements
- **Classification**: **VERIFIED**
- **Source Reference**: [`member-1-science/src/bhnmisntra_science/config.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-1-science/src/bhnmisntra_science/config.py#L432-L488)
- **Verified Fields & Enforced Invariants**:
  1. `investigation_id: str` (enforced non-empty string).
  2. `study_area_id: str` (enforced non-empty string).
  3. `bbox: BoundingBoxWGS84` (requires `min_lon`, `min_lat`, `max_lon`, `max_lat` with $-180 \le \text{lon} \le 180$, $-90 \le \text{lat} \le 90$, $\text{min} < \text{max}$).
  4. `phenomenon_type: Literal["flood", "clearing", "landslide", "coastal"]`.
  5. `expected_behavior: Literal["receding", "sustained"]`.
  6. `reference_acquisition: AcquisitionMetadata`.
  7. `comparison_acquisition: AcquisitionMetadata`.
  8. `subsequent_acquisitions: tuple[AcquisitionMetadata, ...]`.
     - *Hard Validator Invariant* (`validate_inputs`, Line 452): Requires `len(subsequent_acquisitions) >= 3` (`PRD_CONSTANTS.MIN_SUBSEQUENT_FOR_SUPPORTED`). Supplying $<3$ items raises `InsufficientAcquisitionsError`.
  9. `parameters: PipelineParameters` (`polarization`, `calibration_target`, `speckle_filter`, `threshold_strategy`, `mmu_pixels`).
  10. `output_dir: str` (enforced non-empty string).
  11. `confounders: tuple[ConfounderRecord, ...] = ()`.
- **Integrity Validator Invariant** (`validate_investigation_integrity`, Lines 460–488):
  - Enforces `product_id` uniqueness across all acquisitions.
  - Enforces strict geometry compatibility: `(frequency_band, sensor_mode, polarization, look_direction, orbit_direction, relative_orbit)` must match between reference and all comparison/subsequent passes, or raises `GeometryMismatchError`.
- **Finding**: The constructor requirements and strict Pydantic v2 validators stated in the blueprint are fully verified against the source code.

---

### Point 3: Exact `SlicePair` and Raster Input Structures
- **Classification**: **VERIFIED**
- **Source Reference**:
  - `SlicePair`: [`member-1-science/src/bhnmisntra_science/processing/mosaicking.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-1-science/src/bhnmisntra_science/processing/mosaicking.py#L56-L65)
  - `_resolve_acquisition_raster()`: [`member-1-science/src/bhnmisntra_science/pipeline.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-1-science/src/bhnmisntra_science/pipeline.py#L80-L135)
- **Verified Structures**:
  ```python
  @dataclass(frozen=True)
  class SlicePair:
      slice_north: SliceInput | tuple[np.ndarray, AlignmentMetadata] | None
      slice_south: SliceInput | tuple[np.ndarray, AlignmentMetadata] | None
      allow_partial: bool = False
      raise_on_gap: bool = True
  ```
- **Raster Ingestion Resolution**:
  - In `pipeline.py`, `_resolve_acquisition_raster()` natively inspects `slice_data` and `raster_data` for each `product_id`.
  - It explicitly accepts:
    1. Pre-assembled 2D `np.ndarray` float32 + `AlignmentMetadata` tuple.
    2. `SlicePair` instances (automatically concatenated along-track onto `master_grid` via `assemble_abutting_slices()`).
    3. `AssembledRaster` instances.
    4. Dictionary mapping `{"north": ..., "south": ...}`.
- **Finding**: The blueprint's description of along-track slice assembly and dual-format raster ingestion is completely verified.

---

### Point 4: Exact `PipelineExecutionResult` Fields and Types
- **Classification**: **VERIFIED**
- **Source Reference**: [`member-1-science/src/bhnmisntra_science/pipeline.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-1-science/src/bhnmisntra_science/pipeline.py#L60-L78)
- **Verified Class Definition**:
  ```python
  @dataclass(frozen=True)
  class PipelineExecutionResult:
      evidence_status: EvidenceStatus
      classification_reasons: tuple[str, ...]
      beat_test_summary: BeatTestSummary
      baseline_change_stats: dict[str, Any]
      calibration_provenance: dict[str, Any]
      spatial_alignment_verified: bool
      evidence_ledger: dict[str, Any]
      sieved_change_mask: np.ndarray
      diff_raster_db: np.ndarray
      data_authenticity_tier: str
      acquisition_dates: tuple[str, ...] = ()
      temporal_states: tuple[str, ...] = ()
      coverage_metrics: dict[str, Any] = field(default_factory=dict)
      slice_assembly_provenance: dict[str, Any] = field(default_factory=dict)
      scientific_limitations: tuple[str, ...] = ()
      structured_summary: dict[str, Any] = field(default_factory=dict)
  ```
- **Finding**: Exactly 16 fields, their types, defaults, and frozen immutability in the blueprint match the source code definition.

---

### Point 5: Supported Argument: `allow_missing_subsequent`
- **Classification**: **VERIFIED**
- **Source Reference**: [`member-1-science/src/bhnmisntra_science/pipeline.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-1-science/src/bhnmisntra_science/pipeline.py#L220)
- **Verified Implementation Details**:
  - Defined in `run_scientific_pipeline()`: `allow_missing_subsequent: bool = False` (Line 220).
  - Passed down to `_resolve_acquisition_raster()` (Lines 269, 396).
  - In `_resolve_acquisition_raster()` (Lines 85, 107, 126):
    ```python
    if is_subsequent and allow_missing_subsequent:
        return None, None, None
    ```
  - In temporal tracking loop (Lines 420–445): When raster data is `None`, Member 1 assigns `TemporalState.MISSING` and tracks `is_missing=True`.
  - In anti-hallucination gate (Line 463): If valid non-missing passes $< 3$, forces `EvidenceStatus.UNVERIFIED`.
- **Finding**: `allow_missing_subsequent` is a genuine, fully implemented, and tested operational argument.

---

### Point 6: Adapter Construction of Valid Inputs from Backend Data
- **Classification**: **VERIFIED WITH CONDITIONS**
- **Source Reference**:
  - Member 2 Data: [`member-2-backend/backend/data/acquisitions.json`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-2-backend/backend/data/acquisitions.json) & [`study_areas.json`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-2-backend/backend/data/study_areas.json)
  - Member 1 Requirements: [`member-1-science/src/bhnmisntra_science/config.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-1-science/src/bhnmisntra_science/config.py#L39-L135)
- **Verification Analysis**:
  - Member 2's `acquisitions.json` provides: `acquisition_id`, `date`, `datetime`, `mission`, `sensor`, `mode`, `polarization` (as a list `["VV", "VH"]`), `orbit_direction`, `track`, and `valid`.
  - Member 1's `AcquisitionMetadata` requires deeply nested schemas:
    1. `sensor: SensorMetadata`: Requires scalar string `polarization` (adapter must extract `"VV"`), `frequency_band` (missing in Member 2 catalog), `look_direction` (missing in Member 2 catalog), and `incidence_angle: IncidenceAngleMetadata`.
    2. `calibration: CalibrationMetadata`: Discriminated union requiring `RawDnCalibration`, `CalibratedLinearCalibration`, or `CalibratedDbCalibration` with `DigitalNumberConversionDate`, `software_name`, and `lut_name` provenance strings.
    3. `file_path: str`: Mandatory non-empty string.
- **Conditions**:
  The adapter **CAN** construct a valid `InvestigationConfig`, **provided that** `science_adapter.py` supplies standard SAR default templates for Sentinel-1:
  - `frequency_band = "C"`
  - `look_direction = "RIGHT"`
  - `incidence_angle = IncidenceAngleMetadata(quality=IncidenceAngleQuality.AVAILABLE, angle_deg=39.5)`
  - Standard calibrated dB provenance metadata (`CalibratedDbCalibration`).
  Without these defaults, instantiating `AcquisitionMetadata` will fail with Pydantic validation errors.

---

### Point 7: Existence of Genuine Raster Loading Code
- **Classification**: **NOT IMPLEMENTED**
- **Source Reference**:
  - Inspected `member-1-science/src/bhnmisntra_science/`
  - Inspected `member-2-backend/backend/app/`
- **Verification Analysis**:
  - `member-1-science`: Contains zero code importing `rasterio`, `gdal`, or reading `.tif`/`.SAFE` binary archives from disk. In `tests/conftest.py`, rasters are synthesized using `numpy.random.normal()` and `numpy.zeros()`.
  - `member-2-backend`: `layer_service.py` only serves pre-existing files via Starlette `FileResponse`. It does not parse or load raster contents into memory.
- **Finding**: Genuine disk-level raster loading is not implemented in either repository. The pipeline currently executes purely on in-memory synthetic numpy arrays. The blueprint's explicit disclaimer that real-data loading is not yet implemented is accurate.

---

### Point 8: Raster Vectorization & Reprojection via Dependencies
- **Classification**: **VERIFIED WITH CONDITIONS**
- **Source Reference**:
  - Python Environment Audit: `scipy` (Installed), `cv2` (Installed), `pyproj` (NOT INSTALLED), `shapely` (NOT INSTALLED), `rasterio` (NOT INSTALLED).
- **Verification Analysis**:
  - **Vectorization (Mask $\to$ Contours/Polygons)**: **SUPPORTED**. `scipy.ndimage.label` (already used in `beat_test/tracker.py`) and `cv2.findContours` are installed and can extract polygon contours from 2D boolean masks in milliseconds.
  - **Coordinate Reprojection (`EPSG:32643` $\to$ `EPSG:4326`)**: **CONDITIONALLY SUPPORTED**. Because `pyproj` and `rasterio` are not installed, reprojection cannot rely on third-party GIS libraries without installing them.
- **Conditions**:
  Coordinate conversion must be implemented via self-contained mathematical forward transverse Mercator formulas in `science_adapter.py` using Python's standard `math` library (Snyder/Karney equations for UTM Zone 43N), or `pyproj` must be added to `backend/requirements.txt`.

---

### Point 9: `EvidenceLedgerRecord` Scientific Metric Preservation
- **Classification**: **VERIFIED WITH CONDITIONS**
- **Source Reference**: [`member-2-backend/backend/app/schemas/investigation.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-2-backend/backend/app/schemas/investigation.py#L45-L89)
- **Verification Analysis**:
  - `EvidenceLedgerRecord` contains `processing_parameters: Dict[str, Any]` and `evaluation_notes: Optional[str]`, which can store Member 1's nested `audit_checks`, `change_detection_metrics`, and `beat_test_metrics` dictionaries.
  - `changed_area_sq_km: Optional[float]` stores `sieved_change_area_km2`.
  - `reasons_for_label: List[str]` stores Member 1's `classification_reasons`.
  - `persistence_result: str` stores the temporal state summary.
- **Conditions**:
  `EvidenceLedgerRecord` currently has **no dedicated top-level fields** for:
  - `temporal_states: List[str]` (only has `later_acquisition_dates: List[str]`)
  - `surviving_cluster_count: int`
  - `coverage_metrics: Dict[str, Any]`
  These metrics must be placed inside `processing_parameters` or `evaluation_notes` unless optional fields are added to `EvidenceLedgerRecord`.

---

### Point 10: Submodule Structure & Reliable Python Imports
- **Classification**: **VERIFIED WITH CONDITIONS**
- **Source Reference**:
  - Workspace root: `C:\Users\Diya\OneDrive\Apps\bram`
  - Package location: `member-1-science/src/bhnmisntra_science/`
- **Verification Analysis**:
  - `member-1-science` contains no `setup.py` or `pyproject.toml`. Standard `pip install -e ./member-1-science` will fail without build metadata.
  - When running Member 2's FastAPI application (`uvicorn app.main:app`) from `member-2-backend/backend`, `sys.path` does not include `member-1-science/src`.
- **Conditions**:
  Direct `import bhnmisntra_science` will raise `ModuleNotFoundError` unless `science_adapter.py` explicitly injects `member-1-science/src` into `sys.path` at module load time:
  ```python
  import sys
  from pathlib import Path
  _science_src = Path(__file__).resolve().parents[3] / "member-1-science" / "src"
  if _science_src.is_dir() and str(_science_src) not in sys.path:
      sys.path.insert(0, str(_science_src))
  ```
  The blueprint has been updated to mandate this exact path injection pattern.

---

### Point 11: Proposed Execution Endpoint Fits Backend Architecture
- **Classification**: **VERIFIED**
- **Source Reference**: [`member-2-backend/backend/app/routes/investigations.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-2-backend/backend/app/routes/investigations.py) & [`dependencies.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-2-backend/backend/app/dependencies.py)
- **Verification Analysis**:
  - `POST /api/investigations/{investigation_id}/run` uses the identical route signature pattern, regex path validation (`pattern=ID_PATTERN`), security dependency (`dependencies=[Depends(verify_api_key)]`), and tag classification as existing mutation routes (`/investigations`, `/investigations/{id}/evaluate`).
  - Constant-time API key verification (`secrets.compare_digest`) and fail-closed 500 error guards in `dependencies.py` protect the execution endpoint without architectural changes.
- **Finding**: The execution endpoint integrates into Member 2's existing API architecture with zero friction.

---

### Point 12: Temporal Sequence Example Data Authenticity
- **Classification**: **VERIFIED WITH CONDITIONS**
- **Source Reference**:
  - Member 1 Tracker: [`member-1-science/src/bhnmisntra_science/beat_test/tracker.py`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-1-science/src/bhnmisntra_science/beat_test/tracker.py)
  - Member 2 Persistence: [`member-2-backend/backend/data/investigations.json`](file:///C:/Users/Diya/OneDrive/Apps/bram/member-2-backend/backend/data/investigations.json)
- **Verification Analysis**:
  - The 4-state state transition logic (`PEAK` $\to$ `RECEDING` $\to$ `DRAINED`) is mathematically verified by Member 1's unit tests (`test_four_state_tracker.py`, Tests 1–13).
  - However, no real Sentinel-1 pixel time-series data exists in either repository for Kerala, Valencia, or Wayanad.
- **Conditions**:
  Any concrete temporal sequence (e.g. `['PEAK', 'RECEDING', 'RECEDING', 'DRAINED']`) displayed in demonstration ledgers or test outputs is **strictly illustrative and synthetic**. It reflects algorithmic state tracking on synthetic fixtures, not physical measurements from satellite telemetry.

---

## 3. Mandatory Implementation Directives (Derived from Verification)

1. **Adapter Path Injection**: `science_adapter.py` must include dynamic `sys.path.insert(0, str(science_src))` to resolve `bhnmisntra_science` without requiring package installation.
2. **Metadata Templating**: The adapter must inject standard Sentinel-1 C-band geometry defaults (`look_direction="RIGHT"`, `frequency_band="C"`, `polarization="VV"`, calibration provenance) when converting Member 2 catalog records to `InvestigationConfig`.
3. **Self-Contained Reprojection**: Coordinate transformation from `EPSG:32643` to `EPSG:4326` in `science_adapter.py` must use pure-Python Snyder forward equations to avoid uninstalled GIS dependencies (`pyproj`/`rasterio`).
4. **Permanent Provenance Stamping**: The adapter must enforce `data_provenance = "TIER 3 - SYNTHETIC FIXTURE (NOT REAL SATELLITE DATA)"` across all output ledgers, GeoJSON layers, and HTML reports.

---

*End of Integration Architecture Blueprint Verification Report. STOPPED in accordance with instructions.*

