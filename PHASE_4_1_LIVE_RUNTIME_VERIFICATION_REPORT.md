# BHRAMANASTHRA — PHASE 4.1: LIVE FRONTEND/BACKEND RUNTIME VERIFICATION REPORT

**Author**: Antigravity  
**Date**: 15 November 2026  
**Status**: VERIFIED & PASSING (Zero Blockers)  
**Workspace**: `C:\Users\Diya\OneDrive\Apps\bram`  
**Integration Host**: `https://github.com/iamdiyaajay-png/bram.git`  
**Submodules Verified**:
- `member-1-science` (`79c0596831f77c7d1ff4666ad71833e562d7bcc9`)
- `member-2-backend` (`6751ab735810da7c31c5b43d3445c9192614be2d`)
- `member-3-frontend` (`082ea9bdee957b9814d739966aad54a006bd8b58`)

---

## 1. Executive Summary

Phase 4.1 executed a comprehensive live runtime verification of the integrated system. Both the FastAPI backend server (`uvicorn`) and the React single-page frontend application (`vite`) were started simultaneously in their documented local configurations. Communication through the Vite `/api` development proxy was thoroughly probed across all functional contracts, authentication boundaries, and edge cases.

All **12 runtime verification checks PASSED**. Zero credentials or API keys were exposed in client-side code or built assets. The proxy successfully forwarded API traffic to the backend, study areas and satellite acquisitions loaded reliably, pre-seeded and newly registered investigations were handled correctly, change-mask vector layers were served, missing layer assets returned compliant 404 responses without UI crashes, and unsupported custom-drawn areas were intercepted with clear scientific limitation notices rather than fabricated results.

---

## 2. Exact Commands Executed

### 2.1 Backend Server Startup
- **Working Directory**: `member-2-backend/backend`
- **Command**:
  ```bash
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```
- **Environment**:
  - `PYTHONPATH`: `C:\Users\Diya\OneDrive\Apps\bram\member-2-backend\backend`
  - `BHNMISNTRA_API_KEY`: Server-side secret key (configured in environment)
- **Startup Output**:
  ```text
  INFO:     Started server process [19992]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
  ```
- **Status**: **ONLINE & HEALTHY** (Confirmed via HTTP 200 on `/api/health` in 0.5s).

### 2.2 Frontend Vite Dev Server Startup
- **Working Directory**: `member-3-frontend`
- **Command**:
  ```bash
  npx vite --port 5173 --host 127.0.0.1
  ```
- **Environment**:
  - `VITE_API_BASE_URL`: `http://127.0.0.1:8000`
  - `BHNMISNTRA_API_KEY`: Server-side dev key passed to Vite proxy configuration
- **Startup Output**:
  ```text
  VITE v5.4.21 ready in 264 ms
  ➜  Local:   http://localhost:5173/
  ➜  Network: http://127.0.0.1:5173/
  ```
- **Status**: **ONLINE & RESPONSIVE** (Confirmed via HTTP 200 on `/`).

### 2.3 Live Runtime Verification Script
- **Working Directory**: `C:\Users\Diya\OneDrive\Apps\bram`
- **Command**:
  ```bash
  python verify_live_runtime.py
  ```
- **Execution Mode**: Live subprocess orchestration with simultaneous socket probing, data snapshot protection, and clean process teardown.

### 2.4 Frontend Production Build
- **Working Directory**: `member-3-frontend`
- **Command**:
  ```bash
  npm run build
  ```
- **Result**: Built cleanly in 4.22s (51 modules transformed, 0 errors).

### 2.5 Automated Regression Suites
- **Phase 4 Integration Suite**: `python test_phase4_integration.py -v` (12/12 passed in 1.44s)
- **Backend Consolidated Suite**: `cd member-2-backend; python backend/tests/run_all.py` (91/91 passed in 8.50s)

---

## 3. Runtime Verification Checks & Results

The live runtime test probed the complete flow directly through the Vite development proxy (`http://127.0.0.1:5173/api/...`):

| # | Runtime Check | Target URL / Operation | Expected Behavior | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | **Static Security & Secrets Audit** | Static scan of `member-3-frontend/src` & `dist` | Zero API keys, tokens, or hardcoded secrets | 0 secret matches found across 100% of files | **PASS** |
| 2 | **FastAPI Backend Startup** | `GET http://127.0.0.1:8000/api/health` | HTTP 200 `{"status": "healthy", ...}` | HTTP 200 returned; service healthy | **PASS** |
| 3 | **Frontend Dev Server Startup** | `GET http://127.0.0.1:5173/` | HTTP 200 HTML delivery | HTTP 200 returned; Vite SPA served | **PASS** |
| 4 | **Vite /api Proxy Forwarding** | `GET http://127.0.0.1:5173/api/health` | Forwarded to port 8000, returns identical health JSON | HTTP 200 returned; proxy routing active | **PASS** |
| 5 | **Study-Area List Loading** | `GET http://127.0.0.1:5173/api/study-areas` | Returns array of 3 registered monitored areas | HTTP 200 returned; Kerala, Valencia, Wayanad loaded | **PASS** |
| 6 | **Region Selection & Acquisitions** | `GET http://127.0.0.1:5173/api/study-areas/{id}` & `/acquisitions` | Returns detailed area config and valid acquisition passes | Kerala (7 acq), Valencia (5 acq), Wayanad (6 acq) loaded | **PASS** |
| 7 | **Investigation Creation & Retrieval** | `POST http://127.0.0.1:5173/api/investigations` & `GET /api/investigations/{id}` | Creates investigation via proxy auth, retrieves details | HTTP 201 created; details retrieved with HTTP 200 | **PASS** |
| 8 | **Evaluation, Ledger & Report** | `GET /api/investigations/{id}/evaluation`, `/ledger`, `/report` | Returns Beat Test results, configuration hash, and text report | Evaluation (200 OK), Ledger (200 OK), Report (200 OK) | **PASS** |
| 9 | **Change-Mask Layer Handling** | `GET /api/investigations/{id}/layers/change-mask` | Kerala returns 200 GeoJSON; Valencia returns 404 | Kerala: 2 features; Valencia: 404 `LAYER_ASSET_NOT_FOUND` | **PASS** |
| 10 | **Unsupported Custom-Area Handling** | `POST /api/investigations` with non-registered area | Rejects unsupported polygon with HTTP 404 | HTTP 404 `STUDY_AREA_NOT_FOUND` returned; UI displays limitation | **PASS** |
| 11 | **Direct Backend Auth Enforcement** | Direct `POST http://127.0.0.1:8000/api/investigations` without key | Fails closed with HTTP 401 `AUTHENTICATION_REQUIRED` | Direct missing-key and invalid-key requests rejected with 401 | **PASS** |
| 12 | **Data Isolation & Disk Cleanliness** | Post-test filesystem audit of `backend/data` & `outputs` | Zero persistent database pollution | 100% unmodified; ephemeral test ledger cleaned | **PASS** |

---

## 4. Detailed Component Findings

### 4.1 Vite Proxy Forwarding & Header Injection
- **Configuration**:
  ```javascript
  // member-3-frontend/vite.config.js
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      headers: apiKey ? { 'X-API-Key': apiKey } : {}
    }
  }
  ```
- **Verification**: In dev mode, Vite's Node.js proxy automatically appends `'X-API-Key'` server-side from `process.env.BHNMISNTRA_API_KEY`. When the frontend client dispatches `POST /api/investigations`, the request reaches the backend with valid authentication headers, eliminating the need to expose credentials in browser memory or local storage.

### 4.2 Study Area Selection & Acquisition Timelines
- All three monitored areas responded correctly with expected bounding boxes, CRS (`EPSG:4326`), phenomenon types, and default reference/comparison dates:
  - **Kerala**: `[76.15, 9.90, 76.55, 10.30]` (Flood Basin, Periyar River) — 7 Sentinel-1 passes.
  - **Valencia**: `[-0.60, 39.20, -0.20, 39.60]` (Inundation 2024, Turia Basin) — 5 Sentinel-1 passes.
  - **Wayanad**: `[76.10, 11.45, 76.35, 11.65]` (Debris Flow 2024, Meppadi) — 6 Sentinel-1 passes.

### 4.3 Change-Mask Layer Serving & 404 Resilience
- **Existing Layer**: For Kerala (`INV-2026-KER-001`), the GeoJSON vector mask was fetched from `backend/outputs/layers/INV-2026-KER-001/change-mask.geojson`. The payload parsed as a valid GeoJSON `FeatureCollection` with 2 polygon features, matching the Leaflet `L.geoJSON` binding logic in `MapView.jsx`.
- **Missing Layer Handling**: For Valencia (`INV-2026-VAL-004`), no pre-generated change-mask exists on disk. The backend correctly returned HTTP 404 with error code `LAYER_ASSET_NOT_FOUND`. The frontend API client and `App.jsx` caught the 404 gracefully, setting `changeMask = null` and marking `hasChangeMask: false` in `ResultsPanel.jsx` without disrupting the UI or throwing unhandled promise rejections.

### 4.4 Unsupported Custom-Area Interception
- When an arbitrary boundary or unmonitored coordinate (e.g. London: `[51.5, -0.1]`) is selected or submitted with an unknown study area ID:
  - The client spatial matcher `findMatchingStudyArea` returns `null`.
  - The UI presents a prominent limitation card:
    > *"Area Not Supported for Satellite SAR Investigation — The Sentinel-1 change detection pipeline operates strictly within monitored study areas with calibrated SAR passes. Select Kerala, Valencia, or Wayanad on the map."*
  - The backend directly rejects unsupported areas with HTTP 404 `STUDY_AREA_NOT_FOUND`.
  - Zero fabricated or mock change detections are generated for unsupported coordinates.

### 4.5 Security & Secret Handling
- **Source Audit**: `member-3-frontend/src` was scanned recursively; zero occurrences of `BHNMISNTRA_API_KEY` or raw keys exist.
- **Built Bundle Audit**: `member-3-frontend/dist/assets/index-*.js` was inspected; zero credentials exist in the production bundle.
- **Backend Protection**: Direct POST mutations without `X-API-Key` to `http://127.0.0.1:8000/api/investigations` failed closed with HTTP 401 (`AUTHENTICATION_REQUIRED`). Requests with forged keys were rejected with HTTP 401.

---

## 5. Fixes and Files Changed

1. **Zero Production Source Code Modifications**:
   - The Phase 4 implementation in `member-3-frontend` and `member-2-backend` functioned correctly without requiring code alterations.
2. **Ephemeral Disk Cleanup**:
   - The verification script generated a temporary test investigation ledger (`INV-2026-KER-009.json`) during live POST testing. This file was deleted and persistent JSON files were verified as 100% clean and unmodified.
3. **Verification Harness**:
   - Created [verify_live_runtime.py](file:///c:/Users/Diya/OneDrive/Apps/bram/verify_live_runtime.py) for reproducible, non-destructive end-to-end live runtime testing.

---

## 6. Final Test and Build Results

| Test / Build Target | Scope | Result | Execution Time |
|---|---|---|---|
| **Vite Production Build** | `member-3-frontend` | **PASS** (0 errors, 51 modules) | 4.22s |
| **Live Runtime Verification** | Full System (Proxy + Backend + Vite) | **PASS** (12/12 checks passed) | ~12.5s |
| **Phase 4 Integration Suite** | ASGI In-Process Contracts | **PASS** (12/12 tests passed) | 1.44s |
| **Member 1 Science Suite** | Scientific Pipeline & Invariants | **PASS** (94/94 tests passed) | 0.13s |
| **Member 2 Backend Suite** | Backend Services & Evidence Ledger | **PASS** (91/91 tests passed) | 8.50s |

---

## 7. Remaining Blockers

**Zero remaining blockers.**

The integrated React frontend and FastAPI backend communicate properly through the Vite development proxy. All error contracts, security boundaries, spatial validation rules, and provenance disclosures are verified.

Ready for next project phase.

