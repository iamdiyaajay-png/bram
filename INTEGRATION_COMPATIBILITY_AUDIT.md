# BHRAMANASTHRA: Member 1 & Member 2 Deep Integration Compatibility Audit

**Audit Date**: November 15, 2026  
**Auditor**: Antigravity System Architect & Integration Specialist  
**Audited Repositories**:
1. `member-1-science/` (Commit `79c0596`, Branch `main`, Remote: `https://github.com/iamdiyaajay-png/nasa.git`)
2. `member-2-backend/` (Commit `6751ab7`, Branch `main`, Remote: `https://github.com/jasminesunilm1-dotcom/nasa-.git`)  
**Audit Mode**: Read-Only Inspection of Verified Source Code and In-Process Test Execution  
**Integration Status**: 100% Verified Baselines | Pre-Integration Contract Audit Complete  

---

## 1. Verified Repository Details & Baseline Status

| Parameter | Member 1 — Data & Scientific Intelligence | Member 2 — Backend & Evidence Ledger |
| :--- | :--- | :--- |
| **Local Path** | `C:\Users\Diya\OneDrive\Apps\bram\member-1-science` | `C:\Users\Diya\OneDrive\Apps\bram\member-2-backend` |
| **Remote URL** | `https://github.com/iamdiyaajay-png/nasa.git` | `https://github.com/jasminesunilm1-dotcom/nasa-.git` |
| **Git Branch** | `main` (Clean working tree) | `main` (Clean working tree) |
| **Commit ID** | `79c0596831f77c7d1ff4666ad71833e562d7bcc9` | `6751ab735810da7c31c5b43d3445c9192614be2d` |
| **Commit Message**| `docs(status): update status milestone and commit hash in project brain` | `docs: establish official NASA Space Apps 2026 compliance documentation (COMPLIANCE.md)` |
| **Primary Framework**| Python Scientific Kernel (`numpy`, `scipy`, `pydantic v2`) | FastAPI 0.162.6, Starlette 1.10.0, Pydantic 2.14.3 |
| **Verified Test Suite**| **94 / 94 Passed** (`tests/run_tests.py`, 0.075s execution) | **91 / 91 Passed** (`backend/tests/run_all.py`, 14.18s execution) |
| **Handoff Document**| `INTEGRATION_HANDOFF.md` (33.7 KB, Frozen & Validated) | `INTEGRATION_HANDOFF.md` (18.9 KB, Locked) |
| **Data Footprint Guard**| Stateless compute engine (zero disk mutations during test) | In-process test runner with pre/post data footprint hashing |

---

## 2. Runtime and Dependencies Audit

### 2.1 Python Runtime Compatibility
- **Member 1 Requirement**: Python **3.10+** (verified on Python 3.11.9).
- **Member 2 Requirement**: Python **3.12+** (tested on Python 3.12.10).
- **Host System Discovery**:
  - Python 3.11: `C:\Users\Diya\AppData\Local\Programs\Python\Python311\python.exe`
  - Python 3.12: `C:\Users\Diya\AppData\Local\Programs\Python\Python312\python.exe`
  - Python 3.13: `C:\Users\Diya\AppData\Local\Programs\Python\Python313\python.exe`
- **Verification Finding**: Both Member 1's 94 tests and Member 2's 91 tests executed and passed 100% on the active environment. A **single unified Python 3.12 environment is completely feasible**.

### 2.2 Dependency Comparison Matrix

| Dependency | Member 1 Version Spec | Member 2 Version Spec | Shared Environment Recommendation | Conflict Risk |
| :--- | :--- | :--- | :--- | :---: |
| `fastapi` | *Not used* | `>=0.115.0` | `fastapi>=0.115.0` | None |
| `uvicorn[standard]`| *Not used* | `>=0.30.0` | `uvicorn[standard]>=0.30.0` | None |
| `pydantic` | `>=2.0.0` (Pydantic v2) | `>=2.9.0` (Pydantic v2) | `pydantic>=2.9.0,<3.0.0` | **None** (Fully compatible v2) |
| `python-multipart` | *Not used* | `>=0.0.9` | `python-multipart>=0.0.9` | None |
| `python-dotenv` | *Not used* | `>=1.0.0` | `python-dotenv>=1.0.0` | None |
| `numpy` | `>=1.22.0, <2.0.0` | *Not listed* | `numpy>=1.26.0,<2.0.0` | **Low** (Must remain `<2.0.0` for Member 1 C-API compatibility) |
| `scipy` | `>=1.8.0` | *Not listed* | `scipy>=1.11.0` | None |
| `rasterio` | `>=1.3.0` (Optional GIS) | *Not listed* | Optional for GeoTIFF file I/O | None |

---

## 3. Member 1 Scientific Engine Source Inspection

### 3.1 Package Architecture
- **Root Package**: `bhnmisntra_science` (located at `member-1-science/src/bhnmisntra_science`)
- **Key Modules**:
  - `pipeline.py`: End-to-end pipeline execution and orchestration.
  - `config.py`: Strictly validated Pydantic v2 domain schemas.
  - `constants.py`: Frozen mathematical and physical constants (`PRD_CONSTANTS`).
  - `enums.py`: Strongly typed enumerations (`CalibrationState`, `EvidenceStatus`, `TemporalState`, etc.).
  - `policies.py`: Physical classification rules, incidence angle tolerances, and confounder evaluation.
  - `processing/`:
    - `alignment.py`: Affine transform and master cartographic grid alignment.
    - `calibration.py`: Product-aware radiometric calibration with double-calibration guard.
    - `log_ratio.py`: Log-ratio change detection and thresholding (Fixed dB, Robust MAD, Otsu).
    - `mosaicking.py`: Direct abutting along-track slice assembly (`SlicePair`, `assemble_abutting_slices`).
    - `speckle.py`: Linear-power Lee and Boxcar speckle filtering (eliminating log-bias).
  - `beat_test/tracker.py`: Connected-component tracking across $N \ge 3$ passes with the Three-Tier Physical Corroboration Framework.

### 3.2 Primary Entry Point and Public Signature
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

### 3.3 Core Input Schemas
1. **`InvestigationConfig`**:
   - `investigation_id: str`
   - `study_area_id: str`
   - `bbox: BoundingBoxWGS84` (`min_lon`, `min_lat`, `max_lon`, `max_lat`)
   - `phenomenon_type: Literal["flood", "clearing", "landslide", "coastal"]`
   - `expected_behavior: Literal["receding", "sustained"]`
   - `reference_acquisition: AcquisitionMetadata`
   - `comparison_acquisition: AcquisitionMetadata`
   - `subsequent_acquisitions: tuple[AcquisitionMetadata, ...]` (Strict Invariant: Requires $\ge 3$ subsequent acquisitions, enforced by `@model_validator`)
   - `parameters: PipelineParameters`
   - `output_dir: str`
   - `confounders: tuple[ConfounderRecord, ...] = ()`
2. **`AcquisitionMetadata`**:
   - `product_id: str`
   - `acquisition_utc: UtcDatetime`
   - `sensor: SensorMetadata`
   - `orbit: OrbitParameters` (`orbit_number`, `relative_orbit_track`, `pass_direction`, etc.)
   - `calibration: CalibrationMetadata` (`state`, `polarization`, `noise_subtracted`, etc.)
   - `file_path: str`
3. **`raster_data` / `slice_data`**:
   - Mapping from `product_id` to either:
     - Pre-assembled 2D `np.ndarray` float32 + `AlignmentMetadata`
     - Or `SlicePair(slice_north, slice_south)` for abutting along-track scenes

### 3.4 Output Structure: `PipelineExecutionResult`
A frozen dataclass containing:
- `evidence_status: EvidenceStatus` (`SUPPORTED = "supported"`, `INCONCLUSIVE = "inconclusive"`, `UNVERIFIED = "unverified"`)
- `classification_reasons: tuple[str, ...]`
- `beat_test_summary: BeatTestSummary`
- `baseline_change_stats: dict[str, Any]`
- `calibration_provenance: dict[str, Any]`
- `spatial_alignment_verified: bool`
- `evidence_ledger: dict[str, Any]` (Immutable, cryptographic ledger dictionary)
- `sieved_change_mask: np.ndarray` (2D binary array of surviving flood/change pixels)
- `diff_raster_db: np.ndarray` (2D float32 array of backscatter change in decibels)
- `data_authenticity_tier: str`
- `coverage_metrics: dict[str, Any]`
- `slice_assembly_provenance: dict[str, Any]`
- `structured_summary: dict[str, Any]`

---

## 4. Member 2 Backend Source Inspection

### 4.1 Application Architecture
- **Root Package**: `backend/app` (located at `member-2-backend/backend/app`)
- **Key Modules**:
  - `main.py`: FastAPI initialization, CORS origins, Security Headers middleware (CSP, nosniff, SAMEORIGIN).
  - `dependencies.py`: Header-based `X-API-Key` authentication with constant-time comparison and fail-closed 500 error guards.
  - `routes/`:
    - `study_areas.py`: Catalog of monitored regions and satellite acquisitions timeline.
    - `investigations.py`: Investigation creation, detail retrieval, evaluation mutation, layer streaming, and printable report serving.
    - `ledger.py`: Standalone Evidence Ledger JSON retrieval and download endpoints.
  - `schemas/`:
    - `investigation.py`: `InvestigationCreateRequest`, `InvestigationDetail`, `EvidenceLedgerRecord`.
    - `evaluation.py`: `ObservationItem`, `EvaluationRequest`, `EvaluationResponse`.
    - `study_area.py`: `StudyArea`, `Acquisition`, `AcquisitionsResponse`.
    - `errors.py`: Standardized 3-field `ErrorResponse` (`code`, `message`, `suggested_action`).
  - `services/`:
    - `investigation_service.py`: Collision-free ID generation (`INV-YYYY-SLUG-NNN`), atomic JSON persistence (`os.replace`, `os.fsync`), `.corrupt.<timestamp>` recovery.
    - `evidence_service.py`: Tabular Beat Test evaluation and three-state evidence mapping.
    - `layer_service.py`: Spatial asset resolution, path traversal defense, and MIME streaming.
    - `ledger_service.py`: Evidence Ledger JSON export and download packaging.
    - `report_service.py`: Self-contained HTML printable investigation report generator.
    - `study_area_service.py`: Monitored area catalog and geometry filters.

### 4.2 Complete API Route Registry

| Method | Path | Auth Required? | Purpose |
| :--- | :--- | :---: | :--- |
| `GET` | `/` | No | Welcome message and documentation links |
| `GET` | `/api/health` | No | System health check and challenge verification |
| `GET` | `/api/study-areas` | No | List monitored study areas (Kerala, Valencia, Wayanad) |
| `GET` | `/api/study-areas/{study_area_id}` | No | Retrieve single study area details and bounding box |
| `GET` | `/api/study-areas/{study_area_id}/acquisitions` | No | Retrieve satellite pass timeline for study area |
| `POST` | `/api/investigations` | **Yes (`X-API-Key`)** | Create and register a new investigation |
| `GET` | `/api/investigations/{investigation_id}` | No | Retrieve full investigation details and ledger status |
| `GET` | `/api/investigations/{investigation_id}/evaluation` | No | Retrieve current Beat Test evaluation and evidence label |
| `POST` | `/api/investigations/{investigation_id}/evaluate` | **Yes (`X-API-Key`)** | Submit observation passes and update ledger |
| `GET` | `/api/investigations/{investigation_id}/layers` | No | List available map layers for an investigation |
| `GET` | `/api/investigations/{investigation_id}/layers/{layer}` | No | Serve requested map layer (GeoJSON, PNG, or GeoTIFF) |
| `GET` | `/api/investigations/{investigation_id}/ledger` | No | Retrieve complete Evidence Ledger JSON |
| `GET` | `/api/investigations/{investigation_id}/ledger/download` | No | Download Evidence Ledger as an attachment file |
| `GET` | `/api/investigations/{investigation_id}/report` | No | Render self-contained, printable HTML report |

### 4.3 Persistence Structure
- Master Registry: `backend/data/investigations.json` (Atomic JSON dictionary keyed by `investigation_id`).
- Pre-seeded Satellite Catalog: `backend/data/acquisitions.json`.
- Monitored Areas: `backend/data/study_areas.json`.
- Persistent Output Folders:
  - `backend/outputs/ledgers/{investigation_id}.json` (Dedicated ledger files).
  - `backend/outputs/layers/{investigation_id}/` (Contains `change-mask.geojson`, `continuous.geojson`, `reference.geojson`, `comparison.geojson`).

---

## 5. Contract Comparison & Incompatibility Analysis

### 5.1 Incompatibility Matrix

| Dimension | Member 1 Science Implementation | Member 2 Backend Implementation | Incompatibility Details & Mismatch |
| :--- | :--- | :--- | :--- |
| **Pipeline Invocation** | `run_scientific_pipeline()` expects validated `InvestigationConfig` + `raster_data` dictionary. | `investigation_service.create_investigation()` only validates metadata and creates a placeholder ledger with `"change_detection_status": "PENDING"`. | Member 2 currently has **zero calls** to Member 1's scientific engine. Science execution is completely uncoupled. |
| **Temporal Model** | 4-State connected-component tracker (`PERSISTENT_STAGNATION`, `RECEDING`, `RE_INUNDATED`, `DRAINED`, `MISSING`) with spatial MMU and meteorological precipitation corroboration. | Tabular Beat Test in `evidence_service.py` based on boolean pass detection (`change_detected: bool`) and threshold ratio ($\ge 2/3$). | Member 2 has no awareness of spatial connected components, sub-sea-level polders, or meteorological corroboration. |
| **Evidence Label Casing** | `EvidenceStatus`: `"supported"`, `"inconclusive"`, `"unverified"` (Strictly lowercase strings). | `EvaluationResponse.evidence_label`: `"Supported"`, `"Inconclusive"`, `"Unverified"` (Title-Case); `verification_status`: `"SUPPORTED"` (Uppercase). | Direct assignment without string normalization will violate Pydantic schema validation and test assertions. |
| **Spatial Layer Formats** | Generates in-memory 2D numpy arrays (`sieved_change_mask`: bool array, `diff_raster_db`: float32 array) on `EPSG:32643` projected UTM grid. | `layer_service.py` expects physical files on disk in `backend/outputs/layers/{id}/` as `EPSG:4326` WGS84 GeoJSON files or GeoTIFF images. | Member 1 does not vectorize numpy rasters into GeoJSON polygons or write `.geojson` files to disk. |
| **Ledger Schema Format** | Hierarchical JSON dictionary with nested `audit_checks`, `change_detection_metrics`, and `beat_test_metrics`. | Flat Pydantic model `EvidenceLedgerRecord` with top-level fields (`satellite_mission`, `sensor`, `track`, `orbit_direction`, `reproduce_command`, `configuration_hash`). | Output formats do not share the same top-level key schema; translation adapter required. |
| **Confounders Representation** | Structured `ConfounderRecord` tuple with `criticality`, `state` (`CLEAR`/`FLAGGED`/`NOT_ASSESSED`), and `exemption` objects. | List of raw string flags: `confounder_flags: Optional[List[str]]` (e.g. `["CLEAR"]` or `["FLAGGED: Scintillation"]`). | Schema mismatch between structured Pydantic models and raw strings. |
| **Study Area Orbit Tracks** | Research and smoke tests use Sentinel-1 Track **165** (Ascending, dual-slice North/South). | Seeded data in `data/acquisitions.json` uses Track **144** (Descending, single pass). | Geometric consistency validation rejects pairing Track 165 with Track 144. |

---

## 6. Real-Data Integrity and Provenance Safeguards

### 6.1 Audit of Existing Test Records
1. **Member 1 (Science)**:
   - Contains zero raw Sentinel-1 `.SAFE` archives or disk-level `.tif` rasters.
   - All tests use synthetic numpy fixtures generated programmatically in `tests/conftest.py` and `tests/test_processing.py`.
   - Every execution records: `data_authenticity_tier = "TIER 3 - SYNTHETIC FIXTURE (NOT REAL SATELLITE DATA)"`.
2. **Member 2 (Backend)**:
   - All 9 pre-seeded investigations (`INV-2026-KER-001` to `008`, `INV-2026-VAL-004`) contain:
     `"data_provenance": "ILLUSTRATIVE — NOT REAL DATA"`.
   - All sample GeoJSON layers in `outputs/layers/` contain:
     `"scientific_disclaimer": "Demonstration vector change mask for NASA Space Apps Challenge 2026. Awaiting Member 1 scientific pipeline processing."`.
   - In `acquisitions.json`, all records are marked `"data_provenance": "ILLUSTRATIVE — NOT REAL DATA"`.

### 6.2 Data Authenticity Anti-Hallucination Safeguards
- **Non-Negotiable Rule**: Illustrative records and synthetic numpy fixtures must NEVER be displayed or claimed as genuine satellite observations.
- **Enforcement Mechanism**:
  1. Any ledger produced by or passed to Member 2 must carry the explicit provenance banner: `ILLUSTRATIVE — NOT REAL DATA` or `TIER 3 - SYNTHETIC FIXTURE`.
  2. The HTML investigation report (`report_service.py`) already contains dedicated visual caution banners for illustrative data; this must remain permanently enabled until genuine calibrated GeoTIFFs are ingested.
  3. All API layer responses must include `data_provenance` in their GeoJSON `properties`.

---

## 7. Minimal Adapter Architecture Design

To connect Member 1's compute engine to Member 2's FastAPI backend without modifying either repository's core algorithms, a **Science Integration Adapter** (`science_adapter.py`) must be placed in the backend service layer.

### 7.1 Target Information Flow Architecture

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                    Member 3 — Frontend (Future)                          │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ HTTP REST API (X-API-Key for mutations)
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                    Member 2 — FastAPI Backend                             │
│  - routes/investigations.py: POST /api/investigations                     │
│  - routes/investigations.py: POST /api/investigations/{id}/run            │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ Invokes
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│               Science Integration Adapter (science_adapter.py)            │
│  1. Translates InvestigationCreateRequest + StudyArea -> InvestigationConfig│
│  2. Assembles AcquisitionMetadata (orbit, sensor, calibration)            │
│  3. Resolves/loads raster inputs (calibrated numpy arrays or SlicePairs)   │
│  4. Calls member-1-science: run_scientific_pipeline(config, raster_data) │
│  5. Receives PipelineExecutionResult                                      │
│  6. Vectorizes sieved_change_mask to EPSG:4326 GeoJSON polygons           │
│  7. Normalizes enums (lowercase -> Title-Case / Uppercase)                │
│  8. Maps Member 1 ledger metrics into Member 2 EvidenceLedgerRecord       │
│  9. Writes layers to backend/outputs/layers/{id}/                         │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ Returns PipelineExecutionResult + Mapped Ledger
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│              Member 2 — Evidence Services & Persistence                   │
│  - investigation_service._save_all_investigations() (Atomic JSON)         │
│  - ledger_service (outputs/ledgers/{id}.json)                             │
│  - layer_service (outputs/layers/{id}/change-mask.geojson)                │
│  - report_service (Generates executive printable HTML report)             │
└───────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Adapter Responsibilities
1. **Config Builder**: Maps Member 2's `StudyArea` and `Acquisition` models from `data/study_areas.json` and `data/acquisitions.json` into Member 1's `InvestigationConfig` (including `BoundingBoxWGS84`, `PipelineParameters`, and $\ge 3$ `AcquisitionMetadata` items).
2. **Raster Provider**: Loads in-memory synthetic arrays (or cached GeoTIFFs when available) and formats them into `raster_data: dict[str, tuple[np.ndarray, AlignmentMetadata]]` or `SlicePair` objects.
3. **Polygonizer & Coordinate Transformer**: Converts Member 1's 2D boolean `sieved_change_mask` into GeoJSON `Polygon` features with `EPSG:4326` coordinates, writing `change-mask.geojson` and `continuous.geojson` to `backend/outputs/layers/{investigation_id}/`.
4. **Taxonomy & Casing Normalizer**:
   - `EvidenceStatus.SUPPORTED ("supported")` $\to$ `evidence_label = "Supported"`, `verification_status = "SUPPORTED"`
   - `EvidenceStatus.INCONCLUSIVE ("inconclusive")` $\to$ `evidence_label = "Inconclusive"`, `verification_status = "INCONCLUSIVE"`
   - `EvidenceStatus.UNVERIFIED ("unverified")` $\to$ `evidence_label = "Unverified"`, `verification_status = "UNVERIFIED"`
5. **Ledger Synchronizer**: Takes Member 1's `evidence_ledger` dict and updates Member 2's `EvidenceLedgerRecord` fields (`changed_area_sq_km`, `beat_test_status = "EVALUATED"`, `processing_parameters`, `reasons_for_label`), persisting atomically to `backend/data/investigations.json`.

---

## 8. Integrated Testing Strategy (Zero-False-Claims Protocol)

To test the integrated application thoroughly without falsely claiming real satellite validation:

1. **Synthetic Fixture Pipeline Verification**:
   - Create a deterministic integration test suite (`test_integration_adapter.py`) using Member 1's calibrated synthetic numpy fixtures (`tests/conftest.py`).
   - Verify that running the full flow via FastAPI POST endpoint successfully yields `Supported`, produces valid `change-mask.geojson` files, updates the Evidence Ledger, and generates a printable HTML report.
2. **Provenance Disclosure Invariant**:
   - Every integration test must assert that `data_provenance` contains `"ILLUSTRATIVE"` or `"SYNTHETIC"`.
   - Assert that no test output claims `TIER 1 - REAL SATELLITE DATA` unless genuine verified Sentinel-1 rasters are present.
3. **Isolated Test Execution**:
   - Maintain Member 2's `conftest_base.py` sandboxed temporary filesystem pattern so test runs never pollute production `investigations.json` or competition artifacts.
4. **Dual Test Suite Continuity**:
   - Ensure Member 1's 94 unit/integration tests and Member 2's 91 backend tests continue to pass 100% independently (185 total tests) after adapter wiring.

---

## 9. Protected Files Manifest

The following core files embody fundamental PRD invariants and must **never be rewritten, degraded, or modified**:

### Member 1 (Science) Protected Files:
- `member-1-science/src/bhnmisntra_science/constants.py`: Frozen PRD constants, MMU thresholds, and ratio cross-multipliers.
- `member-1-science/src/bhnmisntra_science/enums.py`: Core scientific domain types (`EvidenceStatus`, `TemporalState`).
- `member-1-science/src/bhnmisntra_science/policies.py`: Mathematical classification decision trees and incidence angle rules.
- `member-1-science/src/bhnmisntra_science/processing/calibration.py`: Radiometric calibration and double-calibration guard.
- `member-1-science/src/bhnmisntra_science/processing/speckle.py`: Linear power speckle filtering (log-bias prevention).
- `member-1-science/src/bhnmisntra_science/processing/mosaicking.py`: Direct abutting slice assembly.
- `member-1-science/src/bhnmisntra_science/beat_test/tracker.py`: Four-state connected-component tracking engine.

### Member 2 (Backend) Protected Files:
- `member-2-backend/backend/app/dependencies.py`: Fail-closed `X-API-Key` authentication.
- `member-2-backend/backend/app/services/investigation_service.py`: Atomic JSON persistence and `.corrupt.<timestamp>` recovery shields.
- `member-2-backend/backend/app/schemas/errors.py`: Standardized 3-field `ErrorResponse` schema.
- `member-2-backend/backend/app/services/layer_service.py`: Directory traversal protection mechanisms.

---

## 10. Recommended Implementation Order

1. **Step 1: Environment Alignment**:
   - Confirm unified Python 3.12 environment with `fastapi`, `pydantic>=2.9`, `numpy<2.0.0`, and `scipy>=1.8.0`.
2. **Step 2: Add Adapter Module**:
   - Create `member-2-backend/backend/app/services/science_adapter.py` implementing the config translation, raster resolution, polygonization, and ledger mapping.
3. **Step 3: Connect Endpoint**:
   - Add `POST /api/investigations/{investigation_id}/run` in `member-2-backend/backend/app/routes/investigations.py` (or enhance `create_investigation`) to trigger the adapter.
4. **Step 4: Vector Layer Export**:
   - Implement the mask-to-GeoJSON converter in the adapter to populate `backend/outputs/layers/{id}/change-mask.geojson` from `sieved_change_mask`.
5. **Step 5: Run Combined Integration Verification**:
   - Execute Member 1's 94 tests, Member 2's 91 tests, plus new end-to-end integration tests to verify complete pipeline execution with zero data pollution.

---

## 11. Questions Requiring Team Decisions

1. **API Trigger Flow**: Should scientific processing be executed synchronously on `POST /api/investigations` (which may take a few seconds), or should it be triggered via a dedicated `POST /api/investigations/{id}/run` endpoint?
2. **Map Layer Representation**: Should Member 3 (Frontend MapLibre GL) consume vector GeoJSON polygons produced by the adapter, or does the team prefer high-resolution GeoTIFF/PNG raster tiles?
3. **Satellite Data Ingestion**: When real Sentinel-1 GeoTIFFs become available, will they be provisioned directly to a local directory (`data/rasters/`) or downloaded on demand via NASA ASF / Earthdata API in Member 2?
4. **Orbit Track Unification**: Will the demonstration focus on Kerala Track 165 (Member 1's dual-slice tested configuration) or Kerala Track 144 (Member 2's seeded acquisition dates)?

---

*End of Deep Integration Compatibility Audit Report. STOPPED after generating report in accordance with instructions.*

