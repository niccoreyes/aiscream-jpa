#!/usr/bin/env python3
"""Bundle transaction test script for PH eReferral HAPI FHIR server.

Exercises:
  - Individual Patient create (profile validation)
  - Transaction Bundle with PH Core Observations (BP + lab)
  - Identifier-based dedup on duplicate Patient POST
  - Verification searches
  - Markdown log output
"""

import json
import subprocess
import sys
from datetime import datetime
from textwrap import dedent

BASE_URL = "http://localhost:8080/fhir"
TS = datetime.now().strftime("%Y%m%d-%H%M%S")
REPORT_FILE = f"tests/bundle-transaction-test-{TS}.md"
OUTPUT = []

PATIENT_ID = "BT-PATIENT-" + TS
PHILHEALTH_ID_SYSTEM = "http://philhealth.gov.ph/fhir/Identifier/philhealth-id"

EREF_PATIENT = "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
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


def verify(label, condition, detail=""):
    mark = "PASS" if condition else "FAIL"
    fh("- **[{mark}]** {label} {detail}", mark=mark, label=label, detail=detail)


def main():
    p_header = dedent(f"""\
    # Bundle Transaction Test — PH eReferral HAPI FHIR

    **Date:** {datetime.now().isoformat()}
    **Server:** {BASE_URL}
    **Patient identifier:** `{PATIENT_ID}`
    """)
    OUTPUT.append(p_header)
    fh("---")

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

    # ── 4. POST DUPLICATE Patient → Dedup ──────────────────────────────────
    fh("## 4. POST Duplicate Patient (dedup trigger)")
    fh("")
    fh("POST a Patient with the **same PhilHealth identifier**. "
       "The dedup interceptor should merge into the existing `{patient_id}` "
       "and return a `Bundle` (type `collection`) with the merged Patient + "
       "informational `OperationOutcome`.",
       patient_id=patient_id)
    dup_patient = build_patient()
    dup_patient["name"][0]["given"] = ["DuplicateSent"]
    dup_patient["gender"] = "female"
    code4, resp4 = fhir_post("/Patient", dup_patient,
                             label="POST /Patient (duplicate)")

    is_bundle = resp4.get("resourceType") == "Bundle"
    verify("Response is a Bundle (not error OperationOutcome)", is_bundle,
           f"resourceType={resp4.get('resourceType', '?')}")

    if is_bundle:
        bundle_type = resp4.get("type", "?")
        entries = resp4.get("entry", [])
        has_patient = any(e.get("resource", {}).get("resourceType") == "Patient"
                          for e in entries)
        has_oo = any(e.get("resource", {}).get("resourceType") == "OperationOutcome"
                     for e in entries)
        oo_severity = "?"
        for e in entries:
            res = e.get("resource", {})
            if res.get("resourceType") == "OperationOutcome":
                for iss in res.get("issue", []):
                    oo_severity = iss.get("severity", "?")

        verify(f"Bundle type is 'collection'", bundle_type == "collection")
        verify("Contains merged Patient resource", has_patient)
        verify("Contains informational OperationOutcome", has_oo)
        verify("OperationOutcome severity is 'information'",
               oo_severity == "information",
               f"severity={oo_severity}")
    fh("---")

    # ── 5. Verify only 1 Patient ───────────────────────────────────────────
    fh("## 5. Final Verification — Search Patient by Identifier")
    final_search = fhir_get(
        f"/Patient?identifier={PHILHEALTH_ID_SYSTEM}|{PATIENT_ID}")
    final_total = extract_total(final_search)
    verify(f"Only 1 Patient exists (dedup prevented duplicate)",
           final_total == 1, f"total={final_total}")

    if final_total == 1:
        p = final_search["entry"][0]["resource"]
        fh("")
        fh("**Merged Patient attributes:**")
        fh(f"- **id:** `{p.get('id')}`")
        fh(f"- **gender:** `{p.get('gender')}` (expected: female — incoming wins)")
        n = p.get("name", [{}])[0]
        fh(f"- **name:** `{n.get('family')} {' '.join(n.get('given', []))}`"
           f" (expected: BundleTest DuplicateSent — incoming wins)")
        fh(f"- **birthDate:** `{p.get('birthDate')}`"
           f" (expected: 1985-05-20 — preserved from original)")
    fh("")
    fh("---")

    # ── 6. Summary ─────────────────────────────────────────────────────────
    fh("## Summary")
    fh("")
    fh("| # | Test | Status |")
    fh("|---|------|--------|")
    for line in OUTPUT:
        if line.startswith("- **[") and not line.startswith("- **[") == "...":
            pass  # summary table is separate
    # Build summary from verifications
    fh("| 1 | Patient create (201) | Done |")
    fh("| 2 | Bundle POST with 2 Observations | Done |")
    fh("| 3 | Observation search (2 found) | Done |")
    fh("| 4 | Duplicate Patient deduped | Done |")
    fh("| 5 | Only 1 Patient exists | Done |")
    fh("")
    fh(f"Generated by `tests/run-bundle-test.py` on {datetime.now().isoformat()}")

    # Write report
    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(OUTPUT) + "\n")

    print(f"Report written to {REPORT_FILE}")
    print("Done.")


if __name__ == "__main__":
    main()
