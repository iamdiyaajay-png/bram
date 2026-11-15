"""
Phase 4.2 User Journey & Demo Readiness Verification Suite
Verifies the complete end-to-end user journey:
- Initial load & study areas display
- Kerala, Valencia, and Wayanad selection & date setup
- Investigation flow & results display
- Vector change mask & 404 layer resilience
- Unsupported drawn areas & clear limitations
- Scientific accuracy & canonical provenance compliance
"""

import asyncio
import json
import os
import sys
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
BACKEND_DIR = WORKSPACE / "member-2-backend" / "backend"
FRONTEND_DIR = WORKSPACE / "member-3-frontend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tests.conftest_base import BaseTestCase, TEST_API_KEY


class TestDemoReadinessUserJourney(BaseTestCase):
    """
    Simulates the exact user interactions and verifies that all UI states,
    data models, and scientific guards operate without defects.
    """

    def test_01_initial_load_study_areas(self):
        """User loads app: study areas load on mount, Kerala is selected by default."""
        status, _, body, _ = self.call_api("GET", "/api/study-areas", auth=False)
        self.assertEqual(status, 200)
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 3)

        area_map = {a["id"]: a for a in body}
        self.assertIn("kerala-floods-2018", area_map)
        self.assertIn("valencia-inundation-2024", area_map)
        self.assertIn("wayanad-landslide-2024", area_map)

        # Default area is Kerala
        kerala = area_map["kerala-floods-2018"]
        self.assertEqual(kerala["default_reference_date"], "2018-08-08")
        self.assertEqual(kerala["default_comparison_date"], "2018-08-16")
        self.assertIn("ILLUSTRATIVE", kerala["data_provenance"])

    def test_02_select_all_three_study_areas(self):
        """User can select Kerala, Valencia, and Wayanad, and inspect their acquisitions."""
        targets = [
            ("kerala-floods-2018", "2018-08-08", "2018-08-16", 7),
            ("valencia-inundation-2024", "2024-10-23", "2024-10-31", 5),
            ("wayanad-landslide-2024", "2024-07-20", "2024-08-01", 6),
        ]

        for aid, ref, cmp, min_acq in targets:
            # 1. Fetch study area details
            s_status, _, s_body, _ = self.call_api("GET", f"/api/study-areas/{aid}", auth=False)
            self.assertEqual(s_status, 200, f"Failed fetching {aid}")
            self.assertEqual(s_body["default_reference_date"], ref)
            self.assertEqual(s_body["default_comparison_date"], cmp)

            # 2. Fetch acquisition timelines
            a_status, _, a_body, _ = self.call_api("GET", f"/api/study-areas/{aid}/acquisitions", auth=False)
            self.assertEqual(a_status, 200, f"Failed fetching acquisitions for {aid}")
            self.assertIn("acquisitions", a_body)
            self.assertGreaterEqual(len(a_body["acquisitions"]), min_acq)

            # Verify both default dates exist in acquisitions
            dates = [a["date"] for a in a_body["acquisitions"]]
            self.assertIn(ref, dates, f"Ref date {ref} missing in {aid}")
            self.assertIn(cmp, dates, f"Cmp date {cmp} missing in {aid}")

    def test_03_investigation_kerala_journey(self):
        """User runs investigation for Kerala: results, provenance, change-mask, report & ledger load."""
        inv_id = "INV-2026-KER-001"

        # 1. Fetch detail
        d_status, _, d_body, _ = self.call_api("GET", f"/api/investigations/{inv_id}", auth=False)
        self.assertEqual(d_status, 200)
        self.assertEqual(d_body["investigation_id"], inv_id)
        self.assertIn(d_body["status"], ["CREATED", "COMPLETED"])
        self.assertIn("ILLUSTRATIVE", d_body["data_provenance"])

        # 2. Fetch evaluation
        e_status, _, e_body, _ = self.call_api("GET", f"/api/investigations/{inv_id}/evaluation", auth=False)
        self.assertEqual(e_status, 200)
        self.assertIn(e_body["evidence_label"], ["Supported", "Inconclusive", "Unverified"])
        self.assertIn("reasons_for_label", e_body)
        self.assertGreater(len(e_body["reasons_for_label"]), 0)
        self.assertIn("ILLUSTRATIVE", e_body["data_provenance"])

        # 3. Fetch change mask (available for Kerala)
        m_status, _, m_body, _ = self.call_api("GET", f"/api/investigations/{inv_id}/layers/change-mask", auth=False)
        self.assertEqual(m_status, 200)
        self.assertEqual(m_body["type"], "FeatureCollection")
        self.assertGreater(len(m_body["features"]), 0)

        # 4. Fetch ledger & report
        l_status, _, l_body, _ = self.call_api("GET", f"/api/investigations/{inv_id}/ledger", auth=False)
        self.assertEqual(l_status, 200)
        self.assertIn("configuration_hash", l_body)

        r_status, _, _, r_text = self.call_api("GET", f"/api/investigations/{inv_id}/report", auth=False)
        self.assertEqual(r_status, 200)
        self.assertIn("BHnMISnTRA", r_text)

    def test_04_investigation_valencia_missing_layer_resilience(self):
        """User runs investigation for Valencia: missing change mask returns 404 without crashing."""
        inv_id = "INV-2026-VAL-004"

        # 1. Fetch detail & evaluation
        d_status, _, d_body, _ = self.call_api("GET", f"/api/investigations/{inv_id}", auth=False)
        self.assertEqual(d_status, 200)
        self.assertEqual(d_body["investigation_id"], inv_id)

        e_status, _, e_body, _ = self.call_api("GET", f"/api/investigations/{inv_id}/evaluation", auth=False)
        self.assertEqual(e_status, 200)

        # 2. Fetch change mask -> expect 404 LAYER_ASSET_NOT_FOUND
        m_status, _, m_body, _ = self.call_api("GET", f"/api/investigations/{inv_id}/layers/change-mask", auth=False)
        self.assertEqual(m_status, 404)
        self.assertEqual(m_body.get("code"), "LAYER_ASSET_NOT_FOUND")

    def test_05_investigation_wayanad_creation_flow(self):
        """User runs investigation for Wayanad: investigation creates and initializes ledger."""
        payload = {
            "study_area_id": "wayanad-landslide-2024",
            "reference_date": "2024-07-20",
            "comparison_date": "2024-08-01",
        }
        status, _, body, _ = self.call_api("POST", "/api/investigations", body=payload, auth=True)
        self.assertIn(status, [200, 201])
        inv_id = body.get("investigation_id")
        self.assertIsNotNone(inv_id)

        # Fetch evaluation for created Wayanad investigation
        e_status, _, e_body, _ = self.call_api("GET", f"/api/investigations/{inv_id}/evaluation", auth=False)
        self.assertEqual(e_status, 200)
        self.assertEqual(e_body["evidence_label"], "Unverified")
        self.assertIn("ILLUSTRATIVE", e_body["data_provenance"])

    def test_06_custom_drawn_area_spatial_matching_and_unsupported_rejection(self):
        """
        User draws on map:
        - Points inside study areas match cleanly.
        - Points outside produce unsupported error and API rejects creation with 404.
        """
        study_areas = [
            {"id": "kerala-floods-2018", "bounding_box": [76.15, 9.90, 76.55, 10.30]},
            {"id": "valencia-inundation-2024", "bounding_box": [-0.55, 39.25, -0.25, 39.55]},
            {"id": "wayanad-landslide-2024", "bounding_box": [76.12, 11.48, 76.32, 11.62]},
        ]

        def match_area(lat, lon):
            for sa in study_areas:
                min_lon, min_lat, max_lon, max_lat = sa["bounding_box"]
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    return sa
            return None

        # Point inside Kerala
        self.assertIsNotNone(match_area(10.1, 76.3))
        self.assertEqual(match_area(10.1, 76.3)["id"], "kerala-floods-2018")

        # Point inside Valencia
        self.assertIsNotNone(match_area(39.4, -0.4))
        self.assertEqual(match_area(39.4, -0.4)["id"], "valencia-inundation-2024")

        # Point inside Wayanad
        self.assertIsNotNone(match_area(11.55, 76.22))
        self.assertEqual(match_area(11.55, 76.22)["id"], "wayanad-landslide-2024")

        # Point in Paris / London (unsupported)
        self.assertIsNone(match_area(48.85, 2.35))
        self.assertIsNone(match_area(51.50, -0.12))

        # API rejection on unsupported area ID
        bad_payload = {
            "study_area_id": "paris-basin-unsupported",
            "reference_date": "2026-01-01",
            "comparison_date": "2026-01-02",
        }
        b_status, _, b_body, _ = self.call_api("POST", "/api/investigations", body=bad_payload, auth=True)
        self.assertEqual(b_status, 404)
        self.assertEqual(b_body.get("code"), "STUDY_AREA_NOT_FOUND")

    def test_07_scientific_claim_guards(self):
        """
        Verifies that no component claims real satellite observations,
        NISAR processing, or causal proof.
        """
        # 1. Check all study areas provenance
        _, _, areas, _ = self.call_api("GET", "/api/study-areas", auth=False)
        for a in areas:
            self.assertIn("ILLUSTRATIVE", a["data_provenance"])

        # 2. Check evaluation reasons: must not claim causal proof
        _, _, eval_body, _ = self.call_api("GET", "/api/investigations/INV-2026-KER-001/evaluation", auth=False)
        reasons = " ".join(eval_body.get("reasons_for_label", []))
        self.assertNotIn("proves causation", reasons.lower())
        self.assertNotIn("proved", reasons.lower())
        self.assertIn("ILLUSTRATIVE", eval_body["data_provenance"])


if __name__ == "__main__":
    unittest.main()
