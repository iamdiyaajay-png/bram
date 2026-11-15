# BHRAMANASTHRA
### NASA Space Apps Challenge 2026 — *Dancing with the SARs*
**Multi-Temporal Synthetic Aperture Radar (SAR) Evidence Validation & Surface Change Intelligence Platform**

---

## 1. Project Overview & Architectural Scope

**BHRAMANASTHRA** (*Bhoomi Nireekshanam & Multi-temporal SAR Intelligence for Surface Change Tracking & Resilience Analysis*) is an architectural demonstration, signal processing, and evidence-tracking platform developed for the **NASA Space Apps Challenge 2026**.

The platform demonstrates how multi-temporal Synthetic Aperture Radar (SAR) backscatter time-series can be processed to evaluate potential surface changes (such as flood inundation or landslide scarring) while mitigating false positives from transient environmental confounders and radar speckle noise.

Crucially, the platform couples physical radar signal processing routines and multi-temporal consistency checks (**Beat Test**) with an immutable **Evidence Ledger** to ensure full algorithmic transparency, auditability, and traceability.

> [!IMPORTANT]
> **Prototype & Demonstration Scope**:
> BHRAMANASTHRA is an engineering prototype and architectural integration demonstration. It demonstrates algorithmic pipelines, API contracts, and user-facing dashboards. **The platform does not currently perform live operational satellite data ingestion, nor does it connect to real-time satellite telemetry.**

---

## 2. Scientific Data Tiers & Provenance Boundaries

To maintain rigorous scientific accuracy, BHRAMANASTHRA strictly differentiates four data and processing tiers:

1. **Implemented Algorithms (Active Code)**:
   - Radiometric calibration pipeline (`RAW_DN` $\rightarrow$ Linear Power $\rightarrow$ Decibels).
   - Linear-space adaptive speckle filtering (Lee filter and Boxcar filter with log-bias prevention).
   - Co-registration and spatial affine transform verification (`EPSG:4326` grid alignment).
   - Spatial tuning split, log-ratio differencing, Robust Median Absolute Deviation (MAD), and Otsu thresholding.
   - Morphological Minimum Mapping Unit (MMU) connected-component sieving.
   - Multi-temporal Beat Test temporal consistency tracker.
   - FastAPI RESTful API server with Pydantic v2 domain schemas and Evidence Ledger generator.
   - React single-page interface with Leaflet vector overlay visualization.

2. **Synthetic Test Fixtures (Automated Verification)**:
   - Deterministic mathematical arrays and synthetic SAR rasters (designated Tier 3 in Member 1 tests) used to verify algorithm invariants, edge cases (e.g. antimeridian coordinates, leap seconds), and contract compliance.

3. **Illustrative Demonstration Records (Pre-Seeded Showcase)**:
   - Pre-seeded baseline investigations and study area catalogs stored in `investigations.json`, `study_areas.json`, and `acquisitions.json` (such as `INV-2026-KER-001` and `INV-2026-KER-008`).
   - All demonstration records carry explicit metadata provenance:
     ```json
     "data_provenance": "ILLUSTRATIVE — NOT REAL DATA"
     ```
   - Used exclusively for UI/UX evaluation and API contract verification.

4. **Real Satellite Observations (Not Currently Ingested)**:
   - Real raw SAR granules (e.g. Copernicus Sentinel-1 GRDH/SLC files or future NISAR L-band/S-band data products) are **not** downloaded, ingested, or processed in real-time in this demonstration environment.

---

## 3. Multi-Repository Submodule Architecture

BHRAMANASTHRA integrates three dedicated engineering submodules into this root integration host (`bram`) via native Git submodules:

```
                               ┌──────────────────────────────────────────────┐
                               │       BHRAMANASTHRA Integration Host         │
                               │  https://github.com/iamdiyaajay-png/bram.git │
                               └──────────────────────┬───────────────────────┘
                                                      │
         ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
         │                                            │                                            │
         ▼                                            ▼                                            ▼
┌─────────────────────────────┐        ┌─────────────────────────────┐        ┌─────────────────────────────┐
│  member-1-science (Kernel)  │        │  member-2-backend (FastAPI) │        │  member-3-frontend (React)  │
│  Data & Signal Intelligence │◄───────┤  API & Evidence Ledger      │◄───────┤  MapUI & Decision Dashboard │
│  Commit: 46adcdd            │        │  Commit: 7df95c1            │        │  Commit: aeea4a6            │
└─────────────────────────────┘        └─────────────────────────────┘        └─────────────────────────────┘
```

### Submodule Directory & Repository Matrix

| Submodule Target | Path | Remote Repository URL | Pinned Commit SHA | Primary Responsibilities |
| :--- | :--- | :--- | :---: | :--- |
| **Member 1 (Science Engine)** | `member-1-science` | [iamdiyaajay-png/nasa](https://github.com/iamdiyaajay-png/nasa.git) | `46adcdd` | • Radiometric calibration & linear speckle filtering<br>• Spatial log-ratio thresholding (Robust MAD / Otsu)<br>• Morphological MMU connected-component sieving<br>• Beat Test temporal consistency logic |
| **Member 2 (API & Ledger)** | `member-2-backend` | [jasminesunilm1-dotcom/nasa-](https://github.com/jasminesunilm1-dotcom/nasa-.git) | `7df95c1` | • FastAPI REST service & OpenAPI schemas<br>• Spatial bounding box matching & study area catalog<br>• API security guard (`X-API-Key`)<br>• Evidence Ledger serialization & layer server |
| **Member 3 (User Interface)** | `member-3-frontend` | [nihaharih2007pixel/BHRAMANASTRA-](https://github.com/nihaharih2007pixel/BHRAMANASTRA-.git) | `aeea4a6` | • React 18 / Vite 5 single-page dashboard<br>• Leaflet GeoJSON layer visualizer<br>• NASA GIBS WMTS raster overlays & MapTiler basemap<br>• Monitored study area selector & acquisition timeline<br>• Evidence badge and audit ledger display |

---

## 4. Monitored Study Areas

The backend registers three validated study areas with cataloged satellite acquisition timelines:

| Study Area ID | Region Name | Phenomena & Expected Behavior | Bounding Box (`EPSG:4326`) | Default Acquisition Pair |
| :--- | :--- | :--- | :--- | :--- |
| `kerala-floods-2018` | **Kerala Flood Basin (Periyar River)** | Flood (Receding inundation) | `[76.15, 9.90, 76.55, 10.30]` | `2018-08-08` (Pre) / `2018-08-16` (Peak) |
| `valencia-inundation-2024` | **Valencia Coastal Plain (DANA Event)** | Flood (Rapid runoff & recession) | `[-0.55, 39.25, -0.25, 39.55]` | `2024-10-23` (Pre) / `2024-10-31` (Peak) |
| `wayanad-landslide-2024` | **Wayanad Hills Scar (Meppadi Region)** | Landslide (Sustained scar) | `[76.12, 11.48, 76.32, 11.62]` | `2024-07-20` (Pre) / `2024-08-01` (Event) |

*System Limitation Guard: If a user draws a custom boundary outside these registered study areas, the frontend displays an explicit limitation notice ("Unsupported Area: This location does not overlap a registered study area") and prevents triggering an investigation, ensuring that fabricated results are never generated.*

---

## 5. Prerequisites & Local Installation

### Prerequisites
- **Python**: Version `3.10+` (recommended `3.11` or `3.12`)
- **Node.js**: Version `20+` or `22+` LTS with `npm`
- **Git**: Version `2.30+`

### 1. Recursive Repository Cloning
Clone the integration host repository and recursively initialize all three child submodules:

```bash
# Clone host repository and initialize all child submodules
git clone --recurse-submodules https://github.com/iamdiyaajay-png/bram.git
cd bram

# If already cloned without --recurse-submodules:
git submodule update --init --recursive
```

### 2. Python Environment Setup
Create a virtual environment and install the root integration dependencies (which links Member 1 in editable mode and installs Member 2 backend dependencies):

```bash
# Create and activate virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

# Install integrated backend & scientific dependencies
pip install -r requirements-integration.txt
```

### 3. Frontend Dependency Setup
Install Node.js dependencies for the Member 3 React application:

```bash
cd member-3-frontend
npm install
cd ..
```

---

## 6. Running the Application Locally

The application runs via two local servers: the FastAPI backend service and the Vite development server (with reverse proxy).

### Terminal 1 — Start FastAPI Backend Server
```bash
cd member-2-backend/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- **Backend Service**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`
- **Health Check Endpoint**: `http://127.0.0.1:8000/api/health`

### Terminal 2 — Start React / Vite Development Server
```bash
cd member-3-frontend
npm run dev
```
- **Frontend Application**: `http://127.0.0.1:5173`
- The Vite development server automatically proxies `/api/*` requests to `http://127.0.0.1:8000/api/*`, injecting the configured authentication header transparently.

---

## 7. Automated Testing & Verification Suite

The BHRAMANASTHRA platform includes **216 automated tests and verification checks** across 5 distinct test suites:

```
========================================================================================
SUITE                                    TEST COUNT   STATUS   SCOPE
========================================================================================
1. Member 1 Science Acceptance Tests         94       PASSED   Calibration, Lee filter, MMU, Beat Test
2. Member 2 Backend Service Tests            91       PASSED   FastAPI endpoints, auth, schemas
3. Phase 4 Frontend-Backend Contracts        12       PASSED   ASGI contract & error handling
4. Phase 4.2 User Journey Verification        7       PASSED   End-to-end flows & scientific guards
5. Phase 4.1 Live Runtime Verification       12       PASSED   Concurrent dual-server proxy routing
----------------------------------------------------------------------------------------
TOTAL TESTS                                 216       PASSED   Zero failures, zero regressions
========================================================================================
```

### Execution Commands

```bash
# 1. Member 1 Science Tests (94 tests)
python member-1-science/tests/run_tests.py

# 2. Member 2 Backend Tests (91 tests)
python member-2-backend/backend/tests/run_all.py

# 3. Phase 4 Frontend-Backend Contract Integration Tests (12 tests)
python test_phase4_integration.py

# 4. Phase 4.2 User Journey & Scientific Claim Guards (7 tests)
python test_user_journey.py

# 5. Phase 4.1 Full Live Runtime Dual-Server Smoke Test (12 checks)
python verify_live_runtime.py

# 6. Frontend Production Build Check
cd member-3-frontend && npm run build && cd ..
```

---

## 8. Actual Backend Evaluation & Evidence Behavior

The platform implements a strict **three-state evidence label model** (`Supported`, `Inconclusive`, or `Unverified`) driven by deterministic rules (PRD Section 9):

### How the Evaluation Operates:
1. **Newly Created Investigations (`POST /api/investigations`)**:
   - Initialized in state **`Unverified`** (`verification_status: "UNVERIFIED"`).
   - Reason: The investigation has been registered and initialized in the Evidence Ledger, but has not yet executed post-event satellite pass evaluation (`beat_test_status: "NOT_YET_PROCESSED"`, `beat_test_result: "NOT_AVAILABLE"`).
2. **Evaluated Baseline Investigations** (e.g. pre-seeded showcase record `INV-2026-KER-008`):
   - Shows state **`Supported`** (`verification_status: "SUPPORTED"`, `beat_test_result: "matches"`).
   - **Crucial Provenance Limitation**: This $3/3$ ($100.0\%$) repeat-detection outcome belongs strictly to an **illustrative, pre-seeded demonstration record** created to verify contract parsing and UI state rendering. It is **not** a result derived from real satellite observations and must **never** be presented or interpreted as empirical scientific validation of the study area or actual ground conditions.
   - Algorithmic criteria satisfied within the synthetic record:
     - Minimum post-event acquisitions met ($\ge 3$ valid satellite passes).
     - Beat Test repeated-detection requirement satisfied ($3/3$ passes, $100.0\%$, meeting the $\ge 66.7\%$ persistence threshold).
     - Confounders clear (no ionospheric noise, extreme weather, or severe topographic distortion flagged).
3. **No Fabricated Confidence Values**:
   - The platform does not claim arbitrary statistical confidence scores (e.g. no "95% confidence" claims). Evidence status is strictly binary or ternary based on observational persistence and environmental confounders.

---

## 9. The Beat Test: Temporal Consistency Analysis

The **Beat Test** is a multi-temporal SAR consistency analysis routine designed to assess observational persistence across multiple satellite passes:

- **What it is**: A temporal pattern verification algorithm that checks whether backscatter differences persist across subsequent satellite orbits (for sustained events like landslides) or follow an expected decay/recession pattern (for receding floods). By evaluating multi-temporal consistency across repeated passes, it helps identify backscatter anomalies that may be inconsistent with transient speckle noise.
- **What it is NOT**: The Beat Test cannot conclusively eliminate sensor artefacts, imaging geometry distortions, or localized speckle anomalies, nor does it prove environmental or physical causation. It evaluates observational consistency against a hypothesized temporal behavior model, but does not replace ground-truth in-situ verification or multi-sensor optical cross-validation.

---

## 10. Demonstration Workflow & Illustrative Layers

1. **Access Dashboard**: Open `http://localhost:5173`.
2. **Select Monitored Area**: Choose **Kerala Flood Basin**, **Valencia Coastal Plain**, or **Wayanad Hills Scar**.
3. **Inspect Timelines**: Review cataloged Sentinel-1 acquisition pass dates for the selected basin.
4. **Initiate Investigation**: Click **"Run SAR Investigation →"** to create or retrieve the investigation record via `/api/investigations`.
5. **Inspect Evidence**:
   - Review Evidence Label (`Unverified` for newly registered investigations; `Supported` for evaluated baseline records).
   - Inspect the amber **Provenance Warning Banner**: `PROVENANCE: ILLUSTRATIVE_DEMO_RECORD`.
6. **Toggle Demonstration Change Mask**:
   - For Kerala, the interface renders an illustrative demonstration vector change mask (`change-mask.geojson`).
   - For Valencia, the interface demonstrates missing-layer resilience (catches backend HTTP 404 without crashing).
7. **Audit & Export**:
   - Click **"Evidence Ledger"** to download the standalone immutable JSON audit record (`outputs/ledgers/{id}.json`).
   - Click **"Printable Report"** to view the read-only summary report (`/report`).

---

## 11. Scientific Disclaimers & Governance Constraints

> [!WARNING]
> **Explicit Provenance Disclosure**:
> All investigation records, metrics, change masks, and audit ledgers in this demonstration repository are **ILLUSTRATIVE DEMONSTRATION RECORDS** (`ILLUSTRATIVE_DEMO_RECORD` / `data_provenance: "ILLUSTRATIVE — NOT REAL DATA"`). They are synthetic demonstration fixtures created for architecture validation, UI contract testing, and algorithmic review. They are **NOT** verified real-time satellite observations.

### Rigorous Governance Boundaries:
- **No Causal Proof Claims**: Temporal consistency does not constitute physical proof of disaster causation.
- **Sensor Assumptions & No Sensor Enforcement**: The current scientific processing algorithms and default parameters are designed around **Copernicus Sentinel-1 C-band** backscatter assumptions (e.g. C-SAR sensor, Interferometric Wide swath mode, VV/VH polarizations), rather than strictly enforcing a specific sensor at the code level. While domain schemas support multi-frequency definitions for future expansion (including NISAR L-band and S-band), NISAR ingestion is not currently active, and the platform does not claim operational multi-sensor ingestion.
- **Speckle Filter Residuals**: Adaptive Lee and Boxcar filters mitigate speckle noise in linear power space without logarithmic bias, but residual spatial noise may remain in steep terrain without high-resolution digital elevation model (DEM) terrain flattening.

---

## 12. Integration Audit & Architectural Reports

Complete step-by-step audit reports documenting each phase of the integration are tracked in the repository root:

- [INTEGRATION_ARCHITECTURE_BLUEPRINT.md](./INTEGRATION_ARCHITECTURE_BLUEPRINT.md) — Comprehensive integration architecture specification
- [PHASE_2_EXECUTION_REPORT.md](./PHASE_2_EXECUTION_REPORT.md) — Host initialization and Member 1 & 2 submodule registration
- [PHASE_3_MEMBER_3_INTEGRATION_REPORT.md](./PHASE_3_MEMBER_3_INTEGRATION_REPORT.md) — Member 3 frontend repository submodule integration
- [PHASE_4_FRONTEND_BACKEND_INTEGRATION_REPORT.md](./PHASE_4_FRONTEND_BACKEND_INTEGRATION_REPORT.md) — Frontend-backend API connectivity and schemas
- [PHASE_4_1_LIVE_RUNTIME_VERIFICATION_REPORT.md](./PHASE_4_1_LIVE_RUNTIME_VERIFICATION_REPORT.md) — Live concurrent runtime dual-server verification
- [PHASE_4_2_DEMO_READINESS_REPORT.md](./PHASE_4_2_DEMO_READINESS_REPORT.md) — User journey and demo readiness audit
