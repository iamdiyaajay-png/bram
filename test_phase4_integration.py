"""
Phase 4 Integration Verification Test Suite
Tests contract alignment between Member 3 frontend expectations and Member 2 FastAPI backend.
Runs in-process ASGI testing with zero disk pollution and zero socket port contention.
"""

import os
import sys
import unittest
from pathlib import Path

# Set up paths
_workspace_root = Path(__file__).resolve().parent
_backend_root = _workspace_root / "member-2-backend" / "backend"
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from tests.conftest_base import BaseTestCase, TEST_API_KEY


class TestPhase4FrontendBackendIntegration(BaseTestCase):
    """
    Validates end-to-end API contracts, response payloads, authentication guards,
    and error handling required by the Member 3 frontend.
    """

    def test_01_health_check_contract(self):
        """GET /api/health returns 200 and healthy status required by apiClient.checkHealth()."""
        status, headers, body, _ = self.call_api("GET", "/api/health", auth=False)
        self.assertEqual(status, 200)
        self.assertEqual(body.get("status"), "healthy")
        self.assertIn("service", body)
        self.assertIn("version", body)

    def test_02_study_areas_contract(self):
        """GET /api/study-areas returns registered areas with bounding_box and phenomenon info."""
        status, headers, body, _ = self.call_api("GET", "/api/study-areas", auth=False)
        self.assertEqual(status, 200)
        self.assertIsInstance(body, list)
        self.assertGreaterEqual(len(body), 3)

        area_ids = [a["id"] for a in body]
        self.assertIn("kerala-floods-2018", area_ids)
        self.assertIn("valencia-inundation-2024", area_ids)
        self.assertIn("wayanad-landslide-2024", area_ids)

        for area in body:
            self.assertIn("id", area)
            self.assertIn("name", area)
            self.assertIn("bounding_box", area)
            self.assertEqual(len(area["bounding_box"]), 4)  # [min_lon, min_lat, max_lon, max_lat]
            self.assertIn("crs", area)
            self.assertIn("phenomenon_type", area)
            self.assertIn("default_reference_date", area)
            self.assertIn("default_comparison_date", area)
            self.assertIn("data_provenance", area)

    def test_03_study_area_acquisitions_contract(self):
        """GET /api/study-areas/{id}/acquisitions returns acquisitions object with acquisition list."""
        status, headers, body, _ = self.call_api(
            "GET", "/api/study-areas/kerala-floods-2018/acquisitions", auth=False
        )
        self.assertEqual(status, 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(body.get("study_area_id"), "kerala-floods-2018")
        self.assertIn("acquisitions", body)
        self.assertIsInstance(body["acquisitions"], list)
        self.assertGreaterEqual(len(body["acquisitions"]), 1)

        # Check first acquisition metadata fields
        first_acq = body["acquisitions"][0]
        self.assertIn("acquisition_id", first_acq)
        self.assertIn("date", first_acq)
        self.assertIn("mission", first_acq)

        # Non-existent study area should return 404
        status_404, _, body_404, _ = self.call_api(
            "GET", "/api/study-areas/nonexistent-area-id/acquisitions", auth=False
        )
        self.assertEqual(status_404, 404)

    def test_04_investigation_creation_auth_guard(self):
        """POST /api/investigations rejects requests missing or invalid X-API-Key."""
        payload = {
            "study_area_id": "kerala-floods-2018",
            "reference_date": "2018-08-08",
            "comparison_date": "2018-08-16",
        }
        # Without header -> 401 Unauthorized
        status_no_key, _, body_no_key, _ = self.call_api(
            "POST", "/api/investigations", body=payload, auth=False
        )
        self.assertEqual(status_no_key, 401)
        self.assertEqual(body_no_key.get("code"), "AUTHENTICATION_REQUIRED")

        # With invalid header -> 401 Unauthorized
        status_bad, _, body_bad, _ = self.call_api(
            "POST",
            "/api/investigations",
            headers={"X-API-Key": "completely-invalid-key"},
            body=payload,
            auth=False,
        )
        self.assertEqual(status_bad, 401)
        self.assertEqual(body_bad.get("code"), "AUTHENTICATION_REQUIRED")

    def test_05_investigation_creation_and_retrieval(self):
        """POST /api/investigations creates/retrieves investigation with valid auth."""
        payload = {
            "study_area_id": "kerala-floods-2018",
            "reference_date": "2018-08-08",
            "comparison_date": "2018-08-16",
        }
        status, _, body, _ = self.call_api(
            "POST",
            "/api/investigations",
            body=payload,
            auth=True,
        )
        self.assertIn(status, [200, 201])
        inv_id = body.get("investigation_id")
        self.assertIsNotNone(inv_id)
        self.assertEqual(body.get("study_area_id"), "kerala-floods-2018")

        # GET /api/investigations/{id}
        status_get, _, body_get, _ = self.call_api(
            "GET", f"/api/investigations/{inv_id}", auth=False
        )
        self.assertEqual(status_get, 200)
        self.assertEqual(body_get.get("investigation_id"), inv_id)
        self.assertEqual(body_get.get("study_area", {}).get("id"), "kerala-floods-2018")

    def test_06_investigation_evaluation_contract(self):
        """GET /api/investigations/{id}/evaluation returns all fields required by ResultsPanel."""
        status, _, body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/evaluation", auth=False
        )
        self.assertEqual(status, 200)

        # Verify fields consumed by ResultsPanel.jsx & App.jsx
        self.assertIn("investigation_id", body)
        self.assertIn("evidence_label", body)  # e.g., "Supported", "Unverified", "Inconclusive"
        self.assertIn("verification_status", body)
        self.assertIn("beat_test_status", body)
        self.assertIn("beat_test_result", body)
        self.assertIn("valid_observations_count", body)
        self.assertIn("detected_observations_count", body)
        self.assertIn("reasons_for_label", body)
        self.assertIn("data_provenance", body)

        # Verify reasons is a non-empty list
        self.assertIsInstance(body.get("reasons_for_label"), list)
        self.assertGreater(len(body.get("reasons_for_label")), 0)

        # Verify detail endpoint provides complementary known_limitations
        status_det, _, body_det, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001", auth=False
        )
        self.assertEqual(status_det, 200)
        ledger = body_det.get("evidence_ledger", {})
        self.assertIn("known_limitations", ledger)
        self.assertIsInstance(ledger["known_limitations"], list)
        self.assertGreater(len(ledger["known_limitations"]), 0)

    def test_07_investigation_ledger_contract(self):
        """GET /api/investigations/{id}/ledger returns evaluation ledger entries."""
        status, _, body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/ledger", auth=False
        )
        self.assertEqual(status, 200)
        self.assertIn("investigation_id", body)
        self.assertIn("study_area_id", body)
        self.assertIn("processing_method", body)
        self.assertIn("configuration_hash", body)
        self.assertIn("reproduce_command", body)
        self.assertIn("environment", body)

    def test_08_change_mask_geojson_layer_contract(self):
        """GET /api/investigations/{id}/layers/change-mask returns valid GeoJSON FeatureCollection."""
        status, headers, body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/layers/change-mask", auth=False
        )
        self.assertEqual(status, 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(body.get("type"), "FeatureCollection")
        self.assertIn("features", body)
        self.assertIsInstance(body["features"], list)
        self.assertGreater(len(body["features"]), 0)

        first_feature = body["features"][0]
        self.assertEqual(first_feature.get("type"), "Feature")
        self.assertIn("geometry", first_feature)
        self.assertIn("properties", first_feature)

    def test_09_investigation_report_contract(self):
        """GET /api/investigations/{id}/report returns formatted text report."""
        status, headers, body, raw_text = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/report", auth=False
        )
        self.assertEqual(status, 200)
        self.assertTrue(len(raw_text) > 0)
        self.assertIn("BHnMISnTRA", raw_text)

    def test_10_invalid_study_area_error_handling(self):
        """POST /api/investigations with invalid study_area_id returns 404."""
        payload = {
            "study_area_id": "nonexistent-study-area",
            "reference_date": "2026-01-01",
            "comparison_date": "2026-01-02",
        }
        status, _, body, _ = self.call_api(
            "POST",
            "/api/investigations",
            body=payload,
            auth=True,
        )
        self.assertEqual(status, 404)
        self.assertEqual(body.get("code"), "STUDY_AREA_NOT_FOUND")

    def test_11_unsupported_drawn_area_spatial_matching(self):
        """
        Validates spatial matching logic used in frontend apiClient.
        Points inside study areas match; points outside return None.
        """
        study_areas = [
            {
                "id": "kerala-floods-2018",
                "bounding_box": [76.15, 9.90, 76.55, 10.30],
            },
            {
                "id": "valencia-inundation-2024",
                "bounding_box": [-0.60, 39.20, -0.20, 39.60],
            },
            {
                "id": "wayanad-landslide-2024",
                "bounding_box": [76.10, 11.45, 76.35, 11.65],
            },
        ]

        def find_matching_study_area(center):
            lat, lon = center[0], center[1]
            for sa in study_areas:
                bbox = sa.get("bounding_box") or sa.get("bbox")
                if bbox and len(bbox) == 4:
                    min_lon, min_lat, max_lon, max_lat = bbox
                    if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                        return sa
            return None

        # Inside Kerala
        self.assertIsNotNone(find_matching_study_area([10.1, 76.3]))
        self.assertEqual(find_matching_study_area([10.1, 76.3])["id"], "kerala-floods-2018")

        # Inside Valencia
        self.assertIsNotNone(find_matching_study_area([39.4, -0.4]))
        self.assertEqual(find_matching_study_area([39.4, -0.4])["id"], "valencia-inundation-2024")

        # Outside all study areas (e.g., London: 51.5, -0.1)
        self.assertIsNone(find_matching_study_area([51.5, -0.1]))

    def test_12_canonical_provenance_disclosure(self):
        """Verifies that evaluation and study area records explicitly disclose illustrative provenance."""
        _, _, eval_body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/evaluation", auth=False
        )
        self.assertIn("data_provenance", eval_body)
        self.assertIn("ILLUSTRATIVE", eval_body["data_provenance"])

        _, _, areas_body, _ = self.call_api("GET", "/api/study-areas", auth=False)
        for area in areas_body:
            self.assertIn("data_provenance", area)
            self.assertIn("ILLUSTRATIVE", area["data_provenance"])


if __name__ == "__main__":
    unittest.main()
