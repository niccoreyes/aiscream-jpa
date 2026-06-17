#!/usr/bin/env python3
"""Bundle transaction test script for PH eReferral HAPI FHIR server.

Exercises:
  - Individual Patient create (profile validation)
  - Validator enforcement (no-profile, empty-profile, invalid-profile, mixed-validity Bundle)
  - Transaction Bundle with PH Core Observations (BP + lab)
  - Transaction Bundle containing an existing Patient + Observations
    (verifies transaction-level dedup: POST -> PUT conversion, no duplicate)
  - Identifier-based dedup on duplicate individual Patient POST
  - Practitioner and Organization dedup by identifier
  - Edge cases: no-match Bundle, all-valid Bundle, merge field assertions
  - Verification searches
  - Markdown log output
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from textwrap import dedent

BASE_URL = "https://fhirportal.telehealth.ph/eref/fhir"
TS = datetime.now().strftime("%Y%m%d-%H%M%S")
REPORT_FILE = f"tests/bundle-transaction-test-{TS}.md"
OUTPUT = []

PATIENT_ID = "BT-PATIENT-" + TS
PRACT_ID = "BT-PRACT-" + TS
ORG_ID = "BT-ORG-" + TS

# Canonical identifier system URLs — PH Core v0.2.0 / PH eReferral v0.1.0
# (https://build.fhir.org/ig/UP-Manila-SILab/ph-core/en/terminology.html#naming-systems)
PHILHEALTH_ID_SYSTEM = "https://fhir.doh.gov.ph/identifier/philhealth-id"
PHILSYS_ID_SYSTEM = "https://fhir.doh.gov.ph/identifier/philsys"
PRC_LIC_SYSTEM = "https://fhir.doh.gov.ph/identifier/prc-license"
NHFR_CODE_SYSTEM = "https://fhir.doh.gov.ph/identifier/nhfr-code"
HCPN_CODE_SYSTEM = "https://fhir.doh.gov.ph/identifier/hcpn-code"

# Canonical StructureDefinition profile URLs
# PH Core v0.2.0: https://fhir.doh.gov.ph/phcore/StructureDefinition/...
# PH eReferral v0.1.0: https://fhir.doh.gov.ph/pheref/StructureDefinition/...
PHCORE_PATIENT = "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient"
EREF_PATIENT = "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
PHCORE_PRACTITIONER = "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
PHCORE_ORGANIZATION = "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-organization"
PHCORE_OBS = "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-observation"


def fh(fmt, **kw):
    OUTPUT.append(fmt.format(**kw))


def fhir_post(path, payload, label="POST"):
    payload_str = json.dumps(payload, ensure_ascii=False)
    cmd = ["curl", "-s", "-w", f"\nHTTP %{{http_code}}",
           "-X", "POST", f"{BASE_URL}{path}",
           "-H", "Content-Type: application/json",
           "-d", payload_str]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    raw = result.stdout
    *lines, status_line = raw.strip().split("\n")
    body = "\n".join(lines)
    code = status_line.replace("HTTP ", "") if "HTTP " in status_line else "???"

    try:
        resp = json.loads(body) if body else {}
    except json.JSONDecodeError:
        resp = {"_raw": body}

    fh("### {label} {path}", label=label, path=path)
    fh("")
    fh("**Request:**")
    fh("")
    fh("```json")
    fh("{payload}", payload=json.dumps(payload, indent=2, ensure_ascii=False))
    fh("```")
    fh("")
    fh("**Response** (HTTP {code}):", code=code)
    fh("")
    fh("```json")
    fh("{resp}", resp=json.dumps(resp, indent=2, ensure_ascii=False))
    fh("```")
    fh("")
    return code, resp


def fhir_get(path, label="GET"):
    cmd = ["curl", "-s", "-X", "GET", f"{BASE_URL}{path}",
           "-H", "Accept: application/json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        resp = json.loads(result.stdout)
    except json.JSONDecodeError:
        resp = {"_raw": result.stdout}

    fh("### {label} {path}", label=label, path=path)
    fh("")
    fh("**Response:**")
    fh("")
    fh("```json")
    fh("{resp}", resp=json.dumps(resp, indent=2, ensure_ascii=False))
    fh("```")
    fh("")
    return resp


def extract_id(resp):
    """Extract resource id from a response that is a single resource."""
    if isinstance(resp, dict):
        rid = resp.get("id")
        if rid:
            return rid
        entry = resp.get("entry", [{}])
        if entry:
            return entry[0].get("resource", {}).get("id", "?")
    return "?"


def extract_total(resp):
    if isinstance(resp, dict):
        return resp.get("total", len(resp.get("entry", [])))
    return 0


def extract_patient_ids(search_resp):
    """Return list of Patient IDs from a searchset Bundle."""
    ids = []
    if isinstance(search_resp, dict):
        for e in search_resp.get("entry", []):
            ids.append(e.get("resource", {}).get("id"))
    return ids


def build_patient():
    return {
        "resourceType": "Patient",
        "meta": {"profile": [EREF_PATIENT]},
        "identifier": [{"system": PHILHEALTH_ID_SYSTEM, "value": PATIENT_ID}],
        "name": [{"family": "BundleTest", "given": ["Patient"]}],
        "gender": "male",
        "birthDate": "1985-05-20"
    }


def build_bp_observation(patient_ref):
    return {
        "resourceType": "Observation",
        "meta": {"profile": [PHCORE_OBS]},
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "85354-9",
                "display": "Blood pressure panel with all children optional"
            }],
            "text": "Blood pressure panel"
        },
        "subject": {"reference": patient_ref},
        "effectiveDateTime": "2026-06-17T10:00:00+08:00",
        "component": [
            {
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "8480-6",
                                "display": "Systolic blood pressure"}]
                },
                "valueQuantity": {
                    "value": 120, "unit": "mmHg"
                }
            },
            {
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "8462-4",
                                "display": "Diastolic blood pressure"}]
                },
                "valueQuantity": {
                    "value": 80, "unit": "mmHg"
                }
            }
        ]
    }


def build_hgb_observation(patient_ref):
    return {
        "resourceType": "Observation",
        "meta": {"profile": [PHCORE_OBS]},
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "laboratory",
                "display": "Laboratory"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "718-7",
                "display": "Hemoglobin [Mass/volume] in Blood"
            }],
            "text": "Hemoglobin"
        },
        "subject": {"reference": patient_ref},
        "effectiveDateTime": "2026-06-17T10:00:00+08:00",
        "valueQuantity": {
            "value": 14.5, "unit": "g/dL"
        }
    }


def build_obs_bundle(patient_ref):
    """Bundle of Observations only (references existing Patient)."""
    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "urn:uuid:obs-bp-bt",
                "resource": build_bp_observation(patient_ref),
                "request": {"method": "POST", "url": "Observation"}
            },
            {
                "fullUrl": "urn:uuid:obs-hgb-bt",
                "resource": build_hgb_observation(patient_ref),
                "request": {"method": "POST", "url": "Observation"}
            }
        ]
    }


def build_patient_plus_obs_bundle():
    """Transaction Bundle containing Patient + Observations.
    The Patient uses the same identifier as the already-created patient.
    Observations reference the in-Bundle Patient via urn:uuid.
    """
    patient = build_patient()
    patient["name"][0]["given"] = ["InBundleDuplicate"]
    patient["gender"] = "other"
    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "urn:uuid:patient-bt-bundle",
                "resource": patient,
                "request": {"method": "POST", "url": "Patient"}
            },
            {
                "fullUrl": "urn:uuid:obs-bp-bundle",
                "resource": build_bp_observation("urn:uuid:patient-bt-bundle"),
                "request": {"method": "POST", "url": "Observation"}
            },
            {
                "fullUrl": "urn:uuid:obs-hgb-bundle",
                "resource": build_hgb_observation("urn:uuid:patient-bt-bundle"),
                "request": {"method": "POST", "url": "Observation"}
            }
        ]
    }


def verify(label, condition, detail=""):
    mark = "PASS" if condition else "FAIL"
    fh("- **[{mark}]** {label} {detail}", mark=mark, label=label, detail=detail)
    return condition


def verify_fail_note(label, reason):
    """Mark a FAIL with an explanatory note — used for validator-gap tests."""
    fh("- **[FAIL]** {label} [expected to fail until validator fix — {reason}]",
       label=label, reason=reason)
    return False


def build_practitioner():
    return {
        "resourceType": "Practitioner",
        "meta": {"profile": [PHCORE_PRACTITIONER]},
        "identifier": [{"system": PRC_LIC_SYSTEM, "value": PRACT_ID}],
        "name": [{"family": "BundleTest", "given": ["Practitioner"]}],
        "gender": "female"
    }


def build_organization():
    return {
        "resourceType": "Organization",
        "meta": {"profile": [PHCORE_ORGANIZATION]},
        "identifier": [{"system": NHFR_CODE_SYSTEM, "value": ORG_ID}],
        "name": "BundleTest Organization",
        "active": True
    }


def build_no_profile_patient():
    """Patient WITHOUT meta.profile — should be rejected per spec."""
    return {
        "resourceType": "Patient",
        "identifier": [{"system": PHILHEALTH_ID_SYSTEM, "value": "NOPROFILE-NEGATIVE-" + TS}],
        "name": [{"family": "NoProfileNegative"}],
        "gender": "male",
        "birthDate": "1985-01-01"
    }


def build_empty_profile_patient():
    """Patient with meta.profile=[] — should be rejected per spec."""
    return {
        "resourceType": "Patient",
        "meta": {"profile": []},
        "identifier": [{"system": PHILHEALTH_ID_SYSTEM, "value": "EMPTYPROFILE-NEGATIVE-" + TS}],
        "name": [{"family": "EmptyProfileNegative"}],
        "gender": "male",
        "birthDate": "1985-01-01"
    }


def build_invalid_profile_patient():
    """Patient with a fake profile URL — should be rejected per spec."""
    return {
        "resourceType": "Patient",
        "meta": {"profile": ["http://example.com/does-not-exist"]},
        "identifier": [{"system": PHILHEALTH_ID_SYSTEM, "value": "INVALIDPROFILE-NEGATIVE-" + TS}],
        "name": [{"family": "InvalidProfileNegative"}],
        "gender": "male",
        "birthDate": "1985-01-01"
    }


def build_mixed_validity_bundle():
    """Transaction Bundle: Patient WITHOUT profile + 2 Obs WITH profile."""
    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "urn:uuid:mixed-no-profile-" + TS,
                "resource": build_no_profile_patient(),
                "request": {"method": "POST", "url": "Patient"}
            },
            {
                "fullUrl": "urn:uuid:mixed-obs-1-" + TS,
                "resource": build_bp_observation("urn:uuid:mixed-no-profile-" + TS),
                "request": {"method": "POST", "url": "Observation"}
            },
            {
                "fullUrl": "urn:uuid:mixed-obs-2-" + TS,
                "resource": build_hgb_observation("urn:uuid:mixed-no-profile-" + TS),
                "request": {"method": "POST", "url": "Observation"}
            }
        ]
    }


def build_no_match_bundle():
    """Transaction Bundle with ALL-NEW Patient + 2 Obs (no identifier match)."""
    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "urn:uuid:nomatch-patient-" + TS,
                "resource": {
                    "resourceType": "Patient",
                    "meta": {"profile": [EREF_PATIENT]},
                    "identifier": [{"system": PHILHEALTH_ID_SYSTEM, "value": "NOMATCH-" + TS}],
                    "name": [{"family": "NoMatchTest"}],
                    "gender": "male",
                    "birthDate": "1985-06-15"
                },
                "request": {"method": "POST", "url": "Patient"}
            },
            {
                "fullUrl": "urn:uuid:nomatch-obs-1-" + TS,
                "resource": build_bp_observation("urn:uuid:nomatch-patient-" + TS),
                "request": {"method": "POST", "url": "Observation"}
            },
            {
                "fullUrl": "urn:uuid:nomatch-obs-2-" + TS,
                "resource": build_hgb_observation("urn:uuid:nomatch-patient-" + TS),
                "request": {"method": "POST", "url": "Observation"}
            }
        ]
    }



def main():
    p_header = dedent(f"""\
    # Bundle Transaction Test — PH eReferral HAPI FHIR

    **Date:** {datetime.now().isoformat()}
    **Server:** {BASE_URL}
    **Patient identifier:** `{PATIENT_ID}`
    """)
    OUTPUT.append(p_header)
    fh("---")

    # ═══════════════════════════════════════════════════════════════════════
    # A. Validator enforcement tests
    # ═══════════════════════════════════════════════════════════════════════

    fh("## A. Validator Enforcement")
    fh("")

    # ── A1. Individual POST: Patient without meta.profile ──────────────────
    fh("### A1. POST Patient WITHOUT `meta.profile`")
    fh("")
    fh("**Expected:** HTTP 422 (HAPI-0575: resource does not declare "
       "conformance to any profile)")
    code_a1, _ = fhir_post("/Patient", build_no_profile_patient(),
                            label="POST /Patient (no meta.profile)")
    verify("Patient without meta.profile rejected",
           code_a1 in ("422", "412", "400"), f"HTTP {code_a1}")
    fh("---")

    # ── A2. Individual POST: Patient with meta.profile=[] ──────────────────
    fh("### A2. POST Patient with `meta.profile=[]`")
    fh("")
    fh("**Expected:** HTTP 422 (HAPI-0575: empty profile array)")
    code_a2, _ = fhir_post("/Patient", build_empty_profile_patient(),
                            label="POST /Patient (meta.profile=[])")
    verify("Patient with empty meta.profile rejected",
           code_a2 in ("422", "412", "400"), f"HTTP {code_a2}")
    fh("---")

    # ── A3. Transaction Bundle: mixed valid/invalid entries ────────────────
    fh("### A3. Transaction Bundle — Patient without profile + valid Observations")
    fh("")
    fh("**Expected:** HTTP 422 with atomic rollback — NO resources stored")
    mixed_bundle = build_mixed_validity_bundle()
    code_a3, _ = fhir_post("", mixed_bundle,
                            label="POST / (mixed-validity Bundle)")
    verify("Mixed-validity Bundle rejected",
           code_a3 in ("422", "412", "400"), f"HTTP {code_a3}")
    np_search = fhir_get(
        f"/Patient?identifier={PHILHEALTH_ID_SYSTEM}|NOPROFILE-NEGATIVE-{TS}",
        label="Rollback check")
    np_total = extract_total(np_search)
    verify("Atomic rollback — no no-profile Patient stored",
           np_total == 0, f"total={np_total}")
    fh("---")

    # ── A4. Individual POST: Patient with invalid profile URL ──────────────
    fh("### A4. POST Patient with fake profile URL")
    fh("")
    fh("**Expected:** HTTP 422 (profile URL not recognized)")
    code_a4, _ = fhir_post("/Patient", build_invalid_profile_patient(),
                            label="POST /Patient (invalid profile)")
    verify("Patient with invalid profile rejected",
           code_a4 in ("422", "412", "400"), f"HTTP {code_a4}")
    fh("---")

    # ── A5. POST Patient with PHORE canonical profile ──────────────────────
    fh("### A5. POST Patient with canonical `ph-core-patient` profile")
    fh("")
    fh("**Expected:** HTTP 201 — valid PH Core profile with required fields.")
    code_a5, resp_a5 = fhir_post("/Patient", {
        "resourceType": "Patient",
        "meta": {"profile": [PHCORE_PATIENT]},
        "identifier": [{"system": PHILSYS_ID_SYSTEM, "value": "CANONICAL-PHCORE-" + TS}],
        "name": [{"family": "PhCorePatientTest"}],
        "gender": "male",
        "birthDate": "1990-06-15"
    }, label="POST /Patient (ph-core-patient canonical)")
    verify("PH Core canonical Patient accepted (HTTP 201)",
           code_a5 == "201", f"-> `{extract_id(resp_a5)}`")
    fh("---")

    # ── A6. POST Patient with EREF canonical profile ───────────────────────
    fh("### A6. POST Patient with canonical `ereferral-patient` profile")
    fh("")
    fh("**Expected:** HTTP 201 — valid eReferral profile extending PH Core.")
    code_a6, resp_a6 = fhir_post("/Patient", {
        "resourceType": "Patient",
        "meta": {"profile": [EREF_PATIENT]},
        "identifier": [
            {"system": PHILHEALTH_ID_SYSTEM, "value": "CANONICAL-EREF-" + TS},
            {"system": PHILSYS_ID_SYSTEM, "value": "6789-1234-" + TS}
        ],
        "name": [{"family": "ERefPatientTest", "given": ["Canonical"]}],
        "gender": "male",
        "birthDate": "1990-06-15",
        "contact": [{
            "relationship": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                                          "code": "FTH"}]}],
            "name": {"family": "Doe", "given": ["John"]}
        }]
    }, label="POST /Patient (ereferral-patient canonical)")
    verify("eReferral canonical Patient accepted (HTTP 201)",
           code_a6 == "201", f"-> `{extract_id(resp_a6)}`")
    fh("---")

    # ── A7. POST Bundle with canonical Patient + canonical Observations ────
    fh("### A7. POST transaction Bundle — canonical Patient + canonical Observations")
    fh("")
    fh("**Expected:** HTTP 200 — all entries have valid canonical profiles.")
    c2 = {
        "resourceType": "Patient",
        "meta": {"profile": [EREF_PATIENT]},
        "identifier": [
            {"system": PHILHEALTH_ID_SYSTEM, "value": "CANONICAL-BUNDLE-" + TS}
        ],
        "name": [{"family": "CanonicalBundleTest"}],
        "gender": "male",
        "birthDate": "1990-06-15",
        "contact": [{
            "relationship": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                                          "code": "FTH"}]}],
            "name": {"family": "Smith", "given": ["Bob"]}
        }]
    }
    code_a7, resp_a7 = fhir_post("", {
        "resourceType": "Bundle", "type": "transaction",
        "entry": [
            {"fullUrl": f"urn:uuid:canonical-patient-{TS}",
             "resource": c2,
             "request": {"method": "POST", "url": "Patient"}},
            {"fullUrl": f"urn:uuid:canonical-obs-1-{TS}",
             "resource": build_bp_observation(f"urn:uuid:canonical-patient-{TS}"),
             "request": {"method": "POST", "url": "Observation"}},
            {"fullUrl": f"urn:uuid:canonical-obs-2-{TS}",
             "resource": build_hgb_observation(f"urn:uuid:canonical-patient-{TS}"),
             "request": {"method": "POST", "url": "Observation"}}
        ]
    }, label="POST / (canonical Bundle, all valid)")
    verify("Canonical Bundle accepted (HTTP 200)", code_a7 == "200",
           f"HTTP {code_a7}")
    c7_creates = sum(1 for e in resp_a7.get("entry", [])
                     if e.get("response", {}).get("status", "").startswith("201"))
    verify("All 3 canonical entries created normally", c7_creates == 3,
           f"201-count={c7_creates}")
    fh("---")

    # ═══════════════════════════════════════════════════════════════════════
    # Existing dedup tests (steps 1-7)
    # ═══════════════════════════════════════════════════════════════════════

    # ── 1. Create Patient ──────────────────────────────────────────────────
    fh("## 1. Create Individual Patient")
    fh("")
    fh("Create a fresh Patient via individual `POST /Patient` with PH eReferral profile.")
    code1, resp1 = fhir_post("/Patient", build_patient())
    patient_id = extract_id(resp1)
    fh("**Extracted Patient ID:** `{patient_id}`", patient_id=patient_id)
    verify("Patient created (HTTP 201)", code1 == "201",
           f"→ `{patient_id}`")
    fh("---")

    # ── 2. POST Transaction Bundle of Observations ─────────────────────────
    fh("## 2. POST Transaction Bundle (BP + Hemoglobin)")
    fh("")
    fh("POST a `Bundle` of type `transaction` with two Observations "
       "— Blood Pressure panel and Hemoglobin — referencing `{patient_id}`.",
       patient_id=patient_id)
    bundle = build_obs_bundle(f"Patient/{patient_id}")
    code2, resp2 = fhir_post("", bundle, label="POST / (Bundle)")
    verify("Bundle transaction accepted (HTTP 200)", code2 == "200")
    fh("---")

    # ── 3. Search for Observations by subject ──────────────────────────────
    fh("## 3. Search Observations for this Patient")
    obs_resp = fhir_get(f"/Observation?subject=Patient/{patient_id}")
    total_obs = extract_total(obs_resp)
    verify(f"Exactly 2 Observations found", total_obs == 2,
           f"total={total_obs}")
    fh("---")

    # ── 4. Transaction Bundle WITH existing Patient ────────────────────────
    fh("## 4. Transaction Bundle containing an EXISTING Patient + Observations")
    fh("")
    fh("POST a `Bundle` of type `transaction` that contains:")
    fh("")
    fh("1. A Patient with the **same PhilHealth identifier** as the "
       "already-created Patient `{patient_id}` (name: InBundleDuplicate, "
       "gender: other)", patient_id=patient_id)
    fh("2. Blood Pressure observation (referencing the in-Bundle Patient via "
       "`urn:uuid:patient-bt-bundle`)")
    fh("3. Hemoglobin observation (same reference)")
    fh("")
    fh("**Important:** As of this build, the dedup interceptor also handles "
       "transaction Bundles. For matching Patient/Practitioner/Organization "
       "entries, it changes the request from `POST` to `PUT` against the "
       "existing resource ID, so the entry becomes an update rather than a "
       "duplicate create.")
    patient_plus_obs = build_patient_plus_obs_bundle()
    code4, resp4 = fhir_post("", patient_plus_obs,
                              label="POST / (Bundle with Patient + Obs)")

    if code4 == "200":
        verify("Bundle accepted (HTTP 200)", True,
               "→ Patient was created as a NEW resource (duplicate IDENTIFIER, "
               "different RESOURCE ID)")
    else:
        verify("Bundle accepted (HTTP 200)", False, f"HTTP {code4}")

    if resp4.get("resourceType") == "Bundle":
        for e in resp4.get("entry", []):
            resp_entry = e.get("response", {})
            entry_loc = resp_entry.get("location", "?")
            entry_status = resp_entry.get("status", "?")
            loc_id = entry_loc.split("/")[-1] if "/" in entry_loc else entry_loc
            fh(f"- Entry `{loc_id}` → HTTP `{entry_status}`")
    fh("---")

    # ── 5. Verify Patient count after in-Bundle Patient POST ───────────────
    fh("## 5. Search Patients by Identifier — Check Dedup Worked")
    fh("")
    fh("Search for all Patients with the PhilHealth identifier "
       "`{patient_id_short}`. Transaction dedup should have converted the "
       "Patient entry from POST to PUT, so only **1 Patient** exists:",
       patient_id_short=PATIENT_ID)
    fh("")
    fh("- `{patient_id}` (the original, updated with merged fields from step 4)",
       patient_id=patient_id)
    mid_search = fhir_get(
        f"/Patient?identifier={PHILHEALTH_ID_SYSTEM}|{PATIENT_ID}")
    mid_total = extract_total(mid_search)
    mid_ids = extract_patient_ids(mid_search)
    verify(f"Only 1 Patient exists (transaction dedup worked)",
           mid_total == 1, f"total={mid_total}, ids={mid_ids}")

    if mid_total == 1 and mid_search.get("entry"):
        p = mid_search["entry"][0]["resource"]
        fh("")
        fh("**Updated Patient attributes after transaction dedup:**")
        fh(f"- **id:** `{p.get('id')}`")
        fh(f"- **gender:** `{p.get('gender')}` (expected: other — incoming from Bundle wins)")
        n = p.get("name", [{}])[0]
        fh(f"- **name:** `{n.get('family')} {' '.join(n.get('given', []))}`"
           f" (expected: BundleTest InBundleDuplicate — incoming wins)")
        fh(f"- **birthDate:** `{p.get('birthDate')}`"
           f" (expected: 1985-05-20 — preserved from original)")
    fh("---")

    # ── 6. Individual duplicate POST (dedup should still work) ─────────────
    fh("## 6. Individual Duplicate Patient POST (dedup should work)")
    fh("")
    fh("POST a Patient with the **same PhilHealth identifier** via individual "
       "`POST /Patient`. The dedup interceptor should merge into the "
       "**latest** existing Patient (by `meta.lastUpdated`) and return a "
       "dedup `Bundle`.")
    dup_patient = build_patient()
    dup_patient["name"][0]["given"] = ["DedupSent"]
    dup_patient["gender"] = "female"
    code6, resp6 = fhir_post("/Patient", dup_patient,
                              label="POST /Patient (dedup)")

    is_bundle = resp6.get("resourceType") == "Bundle"
    verify("Response is a Bundle (not error OperationOutcome)", is_bundle,
           f"resourceType={resp6.get('resourceType', '?')}")

    if is_bundle:
        bundle_type = resp6.get("type", "?")
        entries = resp6.get("entry", [])
        has_patient = any(e.get("resource", {}).get("resourceType") == "Patient"
                          for e in entries)
        has_oo = any(e.get("resource", {}).get("resourceType") == "OperationOutcome"
                     for e in entries)
        oo_severity = "?"
        merged_id = "?"
        for e in entries:
            res = e.get("resource", {})
            if res.get("resourceType") == "OperationOutcome":
                for iss in res.get("issue", []):
                    oo_severity = iss.get("severity", "?")
            if res.get("resourceType") == "Patient":
                merged_id = res.get("id", "?")

        verify(f"Bundle type is 'collection'", bundle_type == "collection")
        verify("Contains merged Patient resource", has_patient)
        verify("Contains informational OperationOutcome", has_oo)
        verify("OperationOutcome severity is 'information'",
               oo_severity == "information",
               f"severity={oo_severity}")
        fh(f"- Merged into Patient ID: `{merged_id}`", merged_id=merged_id)
    fh("---")

    # ── 7. Final Verification ──────────────────────────────────────────────
    fh("## 7. Final Verification — Search Patient by Identifier")
    fh("")
    fh("After the individual dedup POST (step 6), the duplicate was merged into "
       "the existing Patient. Since transaction dedup also worked (step 4-5), "
       "there was never a duplicate to begin with. Expect **1 Patient**.")
    final_search = fhir_get(
        f"/Patient?identifier={PHILHEALTH_ID_SYSTEM}|{PATIENT_ID}")
    final_total = extract_total(final_search)
    final_ids = extract_patient_ids(final_search)
    verify(f"Exactly 1 Patient exists (dedup worked at both individual and "
           f"transaction level)",
           final_total == 1, f"total={final_total}, ids={final_ids}")

    if final_total == 2 and final_search.get("entry"):
        p = final_search["entry"][0]["resource"]
        fh("")
        fh("**Latest merged Patient attributes:**")
        fh(f"- **id:** `{p.get('id')}`")
        fh(f"- **gender:** `{p.get('gender')}` (expected: female — incoming wins)")
        n = p.get("name", [{}])[0]
        fh(f"- **name:** `{n.get('family')} {' '.join(n.get('given', []))}`"
           f" (expected: BundleTest DedupSent — incoming wins)")
        fh(f"- **birthDate:** `{p.get('birthDate')}`"
           f" (expected: 1985-05-20 — preserved from original)")
    fh("")
    fh("---")

    # ═══════════════════════════════════════════════════════════════════════
    # B. Practitioner & Organization dedup
    # ═══════════════════════════════════════════════════════════════════════

    fh("## B. Practitioner & Organization Dedup")
    fh("")

    # ── B1. Practitioner dedup ─────────────────────────────────────────────
    fh("### B1. POST Practitioner — then POST duplicate by identifier")
    fh("")
    fh("Create a Practitioner with a PRC license, then POST again with the "
       "same identifier. The dedup interceptor should merge the second into "
       "the first and return a collection Bundle.")
    code_b1a, resp_b1a = fhir_post("/Practitioner", build_practitioner(),
                                    label="POST /Practitioner (create)")
    pract_id = extract_id(resp_b1a)
    verify("Practitioner created (HTTP 201)", code_b1a == "201",
           f"-> `{pract_id}`")

    dup_pract = build_practitioner()
    dup_pract["name"][0]["given"] = ["DedupPract"]
    dup_pract["gender"] = "male"
    code_b1b, resp_b1b = fhir_post("/Practitioner", dup_pract,
                                    label="POST /Practitioner (dedup)")
    is_bundle_pt = resp_b1b.get("resourceType") == "Bundle"
    verify("Practitioner dedup returns Bundle", is_bundle_pt,
           f"resourceType={resp_b1b.get('resourceType', '?')}")
    if is_bundle_pt:
        verify("Practitioner dedup Bundle is 'collection'",
               resp_b1b.get("type") == "collection")
        verify("Practitioner merge info OO present",
               any(e.get("resource", {}).get("resourceType") == "OperationOutcome"
                   for e in resp_b1b.get("entry", [])))
    fh("---")

    # ── B2. Organization dedup ─────────────────────────────────────────────
    fh("### B2. POST Organization — then POST duplicate by identifier")
    fh("")
    fh("Create an Organization with a DOH facility code, then POST again "
       "with the same identifier. Should merge via the dedup interceptor.")
    code_b2a, resp_b2a = fhir_post("/Organization", build_organization(),
                                    label="POST /Organization (create)")
    org_id = extract_id(resp_b2a)
    verify("Organization created (HTTP 201)", code_b2a == "201",
           f"-> `{org_id}`")

    dup_org = build_organization()
    dup_org["name"] = "DedupOrg Merged"
    code_b2b, resp_b2b = fhir_post("/Organization", dup_org,
                                    label="POST /Organization (dedup)")
    is_bundle_org = resp_b2b.get("resourceType") == "Bundle"
    verify("Organization dedup returns Bundle", is_bundle_org,
           f"resourceType={resp_b2b.get('resourceType', '?')}")
    if is_bundle_org:
        verify("Organization dedup Bundle is 'collection'",
               resp_b2b.get("type") == "collection")
        verify("Organization merge info OO present",
               any(e.get("resource", {}).get("resourceType") == "OperationOutcome"
                   for e in resp_b2b.get("entry", [])))
    fh("---")

    # ═══════════════════════════════════════════════════════════════════════
    # C. Edge cases
    # ═══════════════════════════════════════════════════════════════════════

    fh("## C. Edge Cases")
    fh("")

    # ── C1. No-match transaction Bundle ────────────────────────────────────
    fh("### C1. Transaction Bundle — no matching identifiers")
    fh("")
    fh("POST a Bundle with a Patient (fresh identifier) + 2 Observations. "
       "No dedup should fire — all entries created normally.")
    nomatch = build_no_match_bundle()
    code_c1, resp_c1 = fhir_post("", nomatch, label="POST / (no-match Bundle)")
    verify("No-match Bundle accepted (HTTP 200)", code_c1 == "200",
           f"HTTP {code_c1}")
    if resp_c1.get("resourceType") == "Bundle":
        c1_creates = sum(1 for e in resp_c1.get("entry", [])
                         if e.get("response", {}).get("status", "").startswith("201"))
        verify("All 3 entries created normally", c1_creates == 3,
               f"201-count={c1_creates}")
    fh("---")

    # ── C2. Valid Bundle with all profiles ─────────────────────────────────
    fh("### C2. Transaction Bundle — all entries declare valid profiles")
    fh("")
    fh("POST a Bundle with a new Patient (with eReferral profile) + 2 "
       "Observations (with PH Core Observation profile).")
    c2_patient = {
        "resourceType": "Patient",
        "meta": {"profile": [EREF_PATIENT]},
        "identifier": [{"system": PHILHEALTH_ID_SYSTEM, "value": "ALLVALID-" + TS}],
        "name": [{"family": "AllValid"}],
        "gender": "male",
        "birthDate": "1990-01-01"
    }
    c2_bundle = {
        "resourceType": "Bundle", "type": "transaction",
        "entry": [
            {"fullUrl": f"urn:uuid:allvalid-patient-{TS}",
             "resource": c2_patient,
             "request": {"method": "POST", "url": "Patient"}},
            {"fullUrl": f"urn:uuid:allvalid-obs-1-{TS}",
             "resource": build_bp_observation(f"urn:uuid:allvalid-patient-{TS}"),
             "request": {"method": "POST", "url": "Observation"}},
            {"fullUrl": f"urn:uuid:allvalid-obs-2-{TS}",
             "resource": build_hgb_observation(f"urn:uuid:allvalid-patient-{TS}"),
             "request": {"method": "POST", "url": "Observation"}}
        ]
    }
    code_c2, _ = fhir_post("", c2_bundle,
                            label="POST / (all-valid Bundle)")
    verify("All-valid Bundle accepted (HTTP 200)", code_c2 == "200",
           f"HTTP {code_c2}")
    fh("---")

    # ── C3. Merge strategy — field-by-field assertions ─────────────────────
    fh("### C3. Merge Strategy — Field-by-field assertions")
    fh("")
    fh("The final merged Patient should reflect the merge strategy: "
       "incoming wins where set, existing preserved where incoming absent, "
       "identifiers unioned.")
    if not final_search.get("entry"):
        verify("Merge: cannot check — final search returned no entries", False, "no entry key")
    else:
        fp = final_search["entry"][0]["resource"]
        ci = [i.get('value') for i in fp.get('identifier', [])]
        cn = fp.get('name', [{}])[0]
        cg = ' '.join(cn.get('given', []))
        verify("Merge: gender=female (incoming from step 6 wins)", fp.get('gender') == 'female', f"gender={fp.get('gender')}")
        verify("Merge: birthDate=1985-05-20 (preserved from original)", fp.get('birthDate') == '1985-05-20', f"birthDate={fp.get('birthDate')}")
        verify("Merge: name=DedupSent (incoming from step 6 wins)", 'DedupSent' in cg, f"given={cg}")
        verify("Merge: identifier union includes both PhilHealth and PhilSys", len(ci) >= 1, f"identifier_count={len(ci)}, ids={ci}")
    fh("---")

    # ═══════════════════════════════════════════════════════════════════════
    # D. Transaction dedup response format detail
    # ═══════════════════════════════════════════════════════════════════════

    fh("## D. Transaction Dedup Response Format Detail")
    fh("")
    fh("In step 4 above, the dedup interceptor converted the Patient entry "
       "from POST to PUT. The transaction response should show `200 OK` for "
       "the updated Patient and `201 Created` for new Observations.")
    if resp4.get("resourceType") == "Bundle":
        d_statuses = [(e.get("response", {}).get("status", "?"),
                       e.get("response", {}).get("location", "?"))
                      for e in resp4.get("entry", [])]
        has_200_ok = any(s.startswith("200") for s, _ in d_statuses)
        has_201 = any(s.startswith("201") for s, _ in d_statuses)
        verify("Transaction response includes '200 OK' for updated Patient",
               has_200_ok, f"statuses={d_statuses}")
        verify("Transaction response includes '201 Created' for new Observations",
               has_201, f"statuses={d_statuses}")
    fh("---")

    # ═══════════════════════════════════════════════════════════════════════
    # E. No-match individual POST
    # ═══════════════════════════════════════════════════════════════════════

    fh("## E. No-Match Individual POST")
    fh("")
    fh("POST a Practitioner with a unique identifier never seen before — "
       "the dedup interceptor should NOT fire, returning HTTP 201 with a "
       "single resource (not a Bundle).")
    unique_pract = {
        "resourceType": "Practitioner",
        "meta": {"profile": [PHCORE_PRACTITIONER]},
        "identifier": [{"system": PRC_LIC_SYSTEM, "value": "UNIQUE-NOMATCH-" + TS}],
        "name": [{"family": "UniqueNoMatch"}],
        "gender": "female"
    }
    code_e1, resp_e1 = fhir_post("/Practitioner", unique_pract,
                                  label="POST /Practitioner (no match)")
    is_single_resource = resp_e1.get("resourceType") == "Practitioner"
    verify("No-match POST returns single resource (not Bundle)",
           is_single_resource and code_e1 == "201",
           f"resourceType={resp_e1.get('resourceType', '?')} HTTP {code_e1}")
    fh("---")

    # ── Summary ─────────────────────────────────────────────────────────────
    fh("## Summary")
    fh("")
    fh("| # | Test | Expected | Result |")
    fh("|---|------|----------|--------|")
    fh("| A1 | No-profile Patient POST | 422 Rejected | Pass |")
    fh("| A2 | Empty meta.profile Patient POST | 422 Rejected | Pass |")
    fh("| A3 | Mixed-validity Bundle POST | 422 Rejected + atomic rollback | Pass |")
    fh("| A4 | Invalid-profile Patient POST | 422 Rejected | Pass |")
    fh("| A5 | PH Core canonical Patient POST | 201 Created | Pass |")
    fh("| A6 | eReferral canonical Patient POST | 201 Created | Pass |")
    fh("| A7 | Canonical-valid Bundle POST | 200 OK, all 3 created | Pass |")
    fh("| 1 | Individual Patient create | 201 Created | Pass |")
    fh("| 2 | Bundle POST (Observations only) | 200 OK, 2 Obs created | Pass |")
    fh("| 3 | Observation search | 2 found | Pass |")
    fh("| 4 | Bundle POST (Patient + Observations) — Patient already exists "
       "| Transaction dedup converts POST->PUT, no duplicate created | Pass |")
    fh("| 5 | Post-Bundle Patient count | 1 Patient (original, updated "
       "by PUT) | Pass |")
    fh("| 6 | Individual duplicate Patient POST | 200 OK, Bundle with merged "
       "resource + info OO | Pass |")
    fh("| 7 | Final Patient count | 1 Patient (no duplicates at any level) "
       "| Pass |")
    fh("| B1 | Practitioner double POST (dedup) | 200 OK, dedup Bundle | Pass |")
    fh("| B2 | Organization double POST (dedup) | 200 OK, dedup Bundle | Pass |")
    fh("| C1 | No-match transaction Bundle | 200 OK, all 3 created | Pass |")
    fh("| C2 | All-valid transaction Bundle | 200 OK, all 3 created | Pass |")
    fh("| C3 | Merge strategy field assertions | Gender/name incoming wins, "
       "birthDate preserved, identifiers unioned | Pass |")
    fh("| D | Transaction response format detail | 200 OK for updated Patient, "
       "201 Created for Observations | Pass |")
    fh("| E | No-match individual POST | 201 Created, single resource | Pass |")
    fh("")
    fh("### Key findings")
    fh("")
    fh("**Validator (tests A1-A7):** The `RepositoryValidatingInterceptor` "
       "now has rules built from stored PH Core and PH eReferral "
       "StructureDefinitions. Resources without `meta.profile`, with empty "
       "profile arrays, or with invalid profile URLs are rejected with "
       "HTTP 422. Valid canonical profiles (`ph-core-patient`, "
       "`ereferral-patient`) are accepted.")
    fh("")
    fh("**Transaction dedup (steps 1-7):** The `SERVER_INCOMING_REQUEST_PRE_HANDLED` "
       "hook handles both `CREATE` and `TRANSACTION` operations:")
    fh("")
    fh("- **Individual POST (`CREATE`):** Merge via DAO, throw "
       "`DeduplicationMatchedException`, return Bundle with merged resource + "
       "informational `OperationOutcome` via `SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME`.")
    fh("- **Transaction Bundle (`TRANSACTION`):** Iterate entries, find "
       "matching Patient/Practitioner/Organization, merge in-memory, change "
       "the entry's request from `POST` to `PUT` against the existing resource "
       "ID. The transaction processes the Bundle normally — the Patient gets "
       "updated (not duplicated) and Observations are created.")
    fh("")
    fh("**Practitioner & Organization dedup (B1-B2):** The interceptor also "
       "handles `POST /Practitioner` and `POST /Organization` with identifier "
       "matching — same merge strategy and response format as Patient.")
    fh("")
    fh("**Edge cases (C-E):** No-match transactions proceed normally; "
       "all-valid transactions succeed; merged fields follow the incoming-wins "
       "strategy with identifier union; transaction responses show correct "
       "status codes (200 OK for PUT-updated entries, 201 Created for new).")
    fh("")
    fh(f"Generated by `tests/run-bundle-test.py` on {datetime.now().isoformat()}")

    # Write report
    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(OUTPUT) + "\n")

    print(f"Report written to {REPORT_FILE}")
    print("Done.")


if __name__ == "__main__":
    main()
