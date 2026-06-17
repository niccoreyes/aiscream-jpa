# Bundle Transaction Test — PH eReferral HAPI FHIR

**Date:** 2026-06-17T10:01:50.578450
**Server:** http://localhost:8080/fhir
**Patient identifier:** `BT-PATIENT-20260617-100150`

---
## 1. Create Individual Patient

Create a fresh Patient via individual `POST /Patient` with PH eReferral profile.
### POST /Patient

**Request:**

```json
{
  "resourceType": "Patient",
  "meta": {
    "profile": [
      "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-100150"
    }
  ],
  "name": [
    {
      "family": "BundleTest",
      "given": [
        "Patient"
      ]
    }
  ],
  "gender": "male",
  "birthDate": "1985-05-20"
}
```

**Response** (HTTP 201):

```json
{
  "resourceType": "Patient",
  "id": "11503",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T02:01:50.595+00:00",
    "profile": [
      "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-100150"
    }
  ],
  "name": [
    {
      "family": "BundleTest",
      "given": [
        "Patient"
      ]
    }
  ],
  "gender": "male",
  "birthDate": "1985-05-20"
}
```

**Extracted Patient ID:** `11503`
- **[PASS]** Patient created (HTTP 201) → `11503`
---
## 2. POST Transaction Bundle (BP + Hemoglobin)

POST a `Bundle` of type `transaction` with two Observations — Blood Pressure panel and Hemoglobin — referencing `11503`.
### POST / (Bundle) 

**Request:**

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:obs-bp-bt",
      "resource": {
        "resourceType": "Observation",
        "meta": {
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-observation"
          ]
        },
        "status": "final",
        "category": [
          {
            "coding": [
              {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
              }
            ]
          }
        ],
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "85354-9",
              "display": "Blood pressure panel with all children optional"
            }
          ],
          "text": "Blood pressure panel"
        },
        "subject": {
          "reference": "Patient/11503"
        },
        "effectiveDateTime": "2026-06-17T10:00:00+08:00",
        "component": [
          {
            "code": {
              "coding": [
                {
                  "system": "http://loinc.org",
                  "code": "8480-6",
                  "display": "Systolic blood pressure"
                }
              ]
            },
            "valueQuantity": {
              "value": 120,
              "unit": "mmHg"
            }
          },
          {
            "code": {
              "coding": [
                {
                  "system": "http://loinc.org",
                  "code": "8462-4",
                  "display": "Diastolic blood pressure"
                }
              ]
            },
            "valueQuantity": {
              "value": 80,
              "unit": "mmHg"
            }
          }
        ]
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    },
    {
      "fullUrl": "urn:uuid:obs-hgb-bt",
      "resource": {
        "resourceType": "Observation",
        "meta": {
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-observation"
          ]
        },
        "status": "final",
        "category": [
          {
            "coding": [
              {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "laboratory",
                "display": "Laboratory"
              }
            ]
          }
        ],
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "718-7",
              "display": "Hemoglobin [Mass/volume] in Blood"
            }
          ],
          "text": "Hemoglobin"
        },
        "subject": {
          "reference": "Patient/11503"
        },
        "effectiveDateTime": "2026-06-17T10:00:00+08:00",
        "valueQuantity": {
          "value": 14.5,
          "unit": "g/dL"
        }
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    }
  ]
}
```

**Response** (HTTP 200):

```json
{
  "resourceType": "Bundle",
  "id": "a8195d00-c8ec-4b00-8486-6f908bf35c30",
  "type": "transaction-response",
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir"
    }
  ],
  "entry": [
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11504/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T02:01:53.675+00:00",
        "outcome": {
          "resourceType": "OperationOutcome",
          "issue": [
            {
              "severity": "information",
              "code": "informational",
              "details": {
                "coding": [
                  {
                    "system": "https://hapifhir.io/fhir/CodeSystem/hapi-fhir-storage-response-code",
                    "code": "SUCCESSFUL_CREATE",
                    "display": "Create succeeded."
                  }
                ]
              },
              "diagnostics": "Successfully created resource \"Observation/11504/_history/1\". Took 2,403ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11505/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T02:01:53.675+00:00",
        "outcome": {
          "resourceType": "OperationOutcome",
          "issue": [
            {
              "severity": "information",
              "code": "informational",
              "details": {
                "coding": [
                  {
                    "system": "https://hapifhir.io/fhir/CodeSystem/hapi-fhir-storage-response-code",
                    "code": "SUCCESSFUL_CREATE",
                    "display": "Create succeeded."
                  }
                ]
              },
              "diagnostics": "Successfully created resource \"Observation/11505/_history/1\". Took 491ms."
            }
          ]
        }
      }
    }
  ]
}
```

- **[PASS]** Bundle transaction accepted (HTTP 200) 
---
## 3. Search Observations for this Patient
### GET /Observation?subject=Patient/11503

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "82e0a8c6-9d5c-49b1-857d-497cea9bbb48",
  "meta": {
    "lastUpdated": "2026-06-17T02:01:56.680+00:00"
  },
  "type": "searchset",
  "total": 2,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Observation?subject=Patient%2F11503"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Observation/11504",
      "resource": {
        "resourceType": "Observation",
        "id": "11504",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T02:01:53.675+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-observation"
          ]
        },
        "status": "final",
        "category": [
          {
            "coding": [
              {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
              }
            ]
          }
        ],
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "85354-9",
              "display": "Blood pressure panel with all children optional"
            }
          ],
          "text": "Blood pressure panel"
        },
        "subject": {
          "reference": "Patient/11503"
        },
        "effectiveDateTime": "2026-06-17T10:00:00+08:00",
        "component": [
          {
            "code": {
              "coding": [
                {
                  "system": "http://loinc.org",
                  "code": "8480-6",
                  "display": "Systolic blood pressure"
                }
              ]
            },
            "valueQuantity": {
              "value": 120,
              "unit": "mmHg"
            }
          },
          {
            "code": {
              "coding": [
                {
                  "system": "http://loinc.org",
                  "code": "8462-4",
                  "display": "Diastolic blood pressure"
                }
              ]
            },
            "valueQuantity": {
              "value": 80,
              "unit": "mmHg"
            }
          }
        ]
      },
      "search": {
        "mode": "match"
      }
    },
    {
      "fullUrl": "http://localhost:8080/fhir/Observation/11505",
      "resource": {
        "resourceType": "Observation",
        "id": "11505",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T02:01:53.675+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-observation"
          ]
        },
        "status": "final",
        "category": [
          {
            "coding": [
              {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "laboratory",
                "display": "Laboratory"
              }
            ]
          }
        ],
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "718-7",
              "display": "Hemoglobin [Mass/volume] in Blood"
            }
          ],
          "text": "Hemoglobin"
        },
        "subject": {
          "reference": "Patient/11503"
        },
        "effectiveDateTime": "2026-06-17T10:00:00+08:00",
        "valueQuantity": {
          "value": 14.5,
          "unit": "g/dL"
        }
      },
      "search": {
        "mode": "match"
      }
    }
  ]
}
```

- **[PASS]** Exactly 2 Observations found total=2
---
## 4. POST Duplicate Patient (dedup trigger)

POST a Patient with the **same PhilHealth identifier**. The dedup interceptor should merge into the existing `11503` and return a `Bundle` (type `collection`) with the merged Patient + informational `OperationOutcome`.
### POST /Patient (duplicate) /Patient

**Request:**

```json
{
  "resourceType": "Patient",
  "meta": {
    "profile": [
      "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-100150"
    }
  ],
  "name": [
    {
      "family": "BundleTest",
      "given": [
        "DuplicateSent"
      ]
    }
  ],
  "gender": "female",
  "birthDate": "1985-05-20"
}
```

**Response** (HTTP 200):

```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "total": 2,
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "11503",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T02:01:56.778+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-100150"
          }
        ],
        "name": [
          {
            "family": "BundleTest",
            "given": [
              "DuplicateSent"
            ]
          }
        ],
        "gender": "female",
        "birthDate": "1985-05-20"
      },
      "response": {
        "status": "200"
      }
    },
    {
      "resource": {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "information",
            "code": "informational",
            "diagnostics": "Merged incoming Patient into existing resource Patient/11503"
          }
        ]
      },
      "response": {
        "status": "200"
      }
    }
  ]
}
```

- **[PASS]** Response is a Bundle (not error OperationOutcome) resourceType=Bundle
- **[PASS]** Bundle type is 'collection' 
- **[PASS]** Contains merged Patient resource 
- **[PASS]** Contains informational OperationOutcome 
- **[PASS]** OperationOutcome severity is 'information' severity=information
---
## 5. Final Verification — Search Patient by Identifier
### GET /Patient?identifier=http://philhealth.gov.ph/fhir/Identifier/philhealth-id|BT-PATIENT-20260617-100150

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "5d591797-81dc-4f92-9606-60a4da1eed9b",
  "meta": {
    "lastUpdated": "2026-06-17T02:01:56.815+00:00"
  },
  "type": "searchset",
  "total": 1,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=http%3A%2F%2Fphilhealth.gov.ph%2Ffhir%2FIdentifier%2Fphilhealth-id%7CBT-PATIENT-20260617-100150"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/11503",
      "resource": {
        "resourceType": "Patient",
        "id": "11503",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T02:01:56.778+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-100150"
          }
        ],
        "name": [
          {
            "family": "BundleTest",
            "given": [
              "DuplicateSent"
            ]
          }
        ],
        "gender": "female",
        "birthDate": "1985-05-20"
      },
      "search": {
        "mode": "match"
      }
    }
  ]
}
```

- **[PASS]** Only 1 Patient exists (dedup prevented duplicate) total=1

**Merged Patient attributes:**
- **id:** `11503`
- **gender:** `female` (expected: female — incoming wins)
- **name:** `BundleTest DuplicateSent` (expected: BundleTest DuplicateSent — incoming wins)
- **birthDate:** `1985-05-20` (expected: 1985-05-20 — preserved from original)

---
## Summary

| # | Test | Status |
|---|------|--------|
| 1 | Patient create (201) | Done |
| 2 | Bundle POST with 2 Observations | Done |
| 3 | Observation search (2 found) | Done |
| 4 | Duplicate Patient deduped | Done |
| 5 | Only 1 Patient exists | Done |

Generated by `tests/run-bundle-test.py` on 2026-06-17T10:01:56.824882
