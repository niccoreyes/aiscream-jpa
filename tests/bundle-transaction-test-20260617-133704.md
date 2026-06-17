# Bundle Transaction Test — PH eReferral HAPI FHIR

**Date:** 2026-06-17T13:37:04.765983
**Server:** http://localhost:8080/fhir
**Patient identifier:** `BT-PATIENT-20260617-133704`

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
      "value": "BT-PATIENT-20260617-133704"
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
  "id": "13594",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T05:37:04.810+00:00",
    "profile": [
      "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-133704"
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

**Extracted Patient ID:** `13594`
- **[PASS]** Patient created (HTTP 201) → `13594`
---
## 2. POST Transaction Bundle (BP + Hemoglobin)

POST a `Bundle` of type `transaction` with two Observations — Blood Pressure panel and Hemoglobin — referencing `13594`.
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
          "reference": "Patient/13594"
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
          "reference": "Patient/13594"
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
  "id": "8c93b44d-f01b-47ae-9c7d-758b092afcfe",
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
        "location": "Observation/13595/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T05:37:04.908+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/13595/_history/1\". Took 4ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/13596/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T05:37:04.908+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/13596/_history/1\". Took 3ms."
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
### GET /Observation?subject=Patient/13594

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "9b565fc7-2ae0-4845-b411-0e94abcc56c2",
  "meta": {
    "lastUpdated": "2026-06-17T05:37:04.969+00:00"
  },
  "type": "searchset",
  "total": 2,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Observation?subject=Patient%2F13594"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Observation/13595",
      "resource": {
        "resourceType": "Observation",
        "id": "13595",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T05:37:04.908+00:00",
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
          "reference": "Patient/13594"
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
      "fullUrl": "http://localhost:8080/fhir/Observation/13596",
      "resource": {
        "resourceType": "Observation",
        "id": "13596",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T05:37:04.908+00:00",
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
          "reference": "Patient/13594"
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
## 4. Transaction Bundle containing an EXISTING Patient + Observations

POST a `Bundle` of type `transaction` that contains:

1. A Patient with the **same PhilHealth identifier** as the already-created Patient `13594` (name: InBundleDuplicate, gender: other)
2. Blood Pressure observation (referencing the in-Bundle Patient via `urn:uuid:patient-bt-bundle`)
3. Hemoglobin observation (same reference)

**Important:** As of this build, the dedup interceptor also handles transaction Bundles. For matching Patient/Practitioner/Organization entries, it changes the request from `POST` to `PUT` against the existing resource ID, so the entry becomes an update rather than a duplicate create.
### POST / (Bundle with Patient + Obs) 

**Request:**

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:patient-bt-bundle",
      "resource": {
        "resourceType": "Patient",
        "meta": {
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-133704"
          }
        ],
        "name": [
          {
            "family": "BundleTest",
            "given": [
              "InBundleDuplicate"
            ]
          }
        ],
        "gender": "other",
        "birthDate": "1985-05-20"
      },
      "request": {
        "method": "POST",
        "url": "Patient"
      }
    },
    {
      "fullUrl": "urn:uuid:obs-bp-bundle",
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
          "reference": "urn:uuid:patient-bt-bundle"
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
      "fullUrl": "urn:uuid:obs-hgb-bundle",
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
          "reference": "urn:uuid:patient-bt-bundle"
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
  "id": "4e7175a0-dcc8-4905-b226-e46d731c9b47",
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
        "status": "200 OK",
        "location": "Patient/13594/_history/2",
        "etag": "2",
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
                    "code": "SUCCESSFUL_UPDATE",
                    "display": "Update succeeded."
                  }
                ]
              },
              "diagnostics": "Successfully updated resource \"Patient/13594/_history/2\"."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/13597/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T05:37:05.007+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/13597/_history/1\". Took 2ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/13598/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T05:37:05.007+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/13598/_history/1\". Took 1ms."
            }
          ]
        }
      }
    }
  ]
}
```

- **[PASS]** Bundle accepted (HTTP 200) → Patient was created as a NEW resource (duplicate IDENTIFIER, different RESOURCE ID)
- Entry `2` → HTTP `200 OK`
- Entry `1` → HTTP `201 Created`
- Entry `1` → HTTP `201 Created`
---
## 5. Search Patients by Identifier — Check Dedup Worked

Search for all Patients with the PhilHealth identifier `BT-PATIENT-20260617-133704`. Transaction dedup should have converted the Patient entry from POST to PUT, so only **1 Patient** exists:

- `13594` (the original, updated with merged fields from step 4)
### GET /Patient?identifier=http://philhealth.gov.ph/fhir/Identifier/philhealth-id|BT-PATIENT-20260617-133704

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "2370aaa5-effa-4aae-b814-363462ba950e",
  "meta": {
    "lastUpdated": "2026-06-17T05:37:05.046+00:00"
  },
  "type": "searchset",
  "total": 1,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=http%3A%2F%2Fphilhealth.gov.ph%2Ffhir%2FIdentifier%2Fphilhealth-id%7CBT-PATIENT-20260617-133704"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/13594",
      "resource": {
        "resourceType": "Patient",
        "id": "13594",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T05:37:05.007+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-133704"
          }
        ],
        "name": [
          {
            "family": "BundleTest",
            "given": [
              "InBundleDuplicate"
            ]
          }
        ],
        "gender": "other",
        "birthDate": "1985-05-20"
      },
      "search": {
        "mode": "match"
      }
    }
  ]
}
```

- **[PASS]** Only 1 Patient exists (transaction dedup worked) total=1, ids=['13594']

**Updated Patient attributes after transaction dedup:**
- **id:** `13594`
- **gender:** `other` (expected: other — incoming from Bundle wins)
- **name:** `BundleTest InBundleDuplicate` (expected: BundleTest InBundleDuplicate — incoming wins)
- **birthDate:** `1985-05-20` (expected: 1985-05-20 — preserved from original)
---
## 6. Individual Duplicate Patient POST (dedup should work)

POST a Patient with the **same PhilHealth identifier** via individual `POST /Patient`. The dedup interceptor should merge into the **latest** existing Patient (by `meta.lastUpdated`) and return a dedup `Bundle`.
### POST /Patient (dedup) /Patient

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
      "value": "BT-PATIENT-20260617-133704"
    }
  ],
  "name": [
    {
      "family": "BundleTest",
      "given": [
        "DedupSent"
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
        "id": "13594",
        "meta": {
          "versionId": "3",
          "lastUpdated": "2026-06-17T05:37:05.103+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-133704"
          }
        ],
        "name": [
          {
            "family": "BundleTest",
            "given": [
              "DedupSent"
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
            "diagnostics": "Merged incoming Patient into existing resource Patient/13594"
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
- Merged into Patient ID: `13594`
---
## 7. Final Verification — Search Patient by Identifier

After the individual dedup POST (step 6), the duplicate was merged into the existing Patient. Since transaction dedup also worked (step 4-5), there was never a duplicate to begin with. Expect **1 Patient**.
### GET /Patient?identifier=http://philhealth.gov.ph/fhir/Identifier/philhealth-id|BT-PATIENT-20260617-133704

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "2370aaa5-effa-4aae-b814-363462ba950e",
  "meta": {
    "lastUpdated": "2026-06-17T05:37:05.046+00:00"
  },
  "type": "searchset",
  "total": 1,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=http%3A%2F%2Fphilhealth.gov.ph%2Ffhir%2FIdentifier%2Fphilhealth-id%7CBT-PATIENT-20260617-133704"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/13594",
      "resource": {
        "resourceType": "Patient",
        "id": "13594",
        "meta": {
          "versionId": "3",
          "lastUpdated": "2026-06-17T05:37:05.103+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-133704"
          }
        ],
        "name": [
          {
            "family": "BundleTest",
            "given": [
              "DedupSent"
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

- **[PASS]** Exactly 1 Patient exists (dedup worked at both individual and transaction level) total=1, ids=['13594']

---
## 8. MDM — Poll for Golden Patient (async)

**Golden Patient found after 21.5s:** `13593`
- **[PASS]** Golden Patient exists within 30 s golden_id=13593
- **[PASS]** Golden has HAPI-MDM tag tags=[{'system': 'http://hapifhir.io/fhir/NamingSystem/mdm-record-status', 'version': '1', 'code': 'GOLDEN_RECORD', 'display': 'Golden Record', 'userSelected': False}, {'system': 'https://hapifhir.org/NamingSystem/managing-mdm-system', 'version': '1', 'code': 'HAPI-MDM', 'display': 'This Golden Resource can only be modified by HAPI MDM system.', 'userSelected': False}]
---
## 9. MDM — Verify server health after MDM processing

**CapabilityStatement available:** OK
- **[PASS]** Server still healthy after MDM processing status=OK
---
## Summary

| # | Test | Expected | Result |
|---|------|----------|--------|
| 1 | Individual Patient create | 201 Created | Pass |
| 2 | Bundle POST (Observations only) | 200 OK, 2 Obs created | Pass |
| 3 | Observation search | 2 found | Pass |
| 4 | Bundle POST (Patient + Observations) — Patient already exists | Transaction dedup converts POST->PUT, no duplicate created | Pass |
| 5 | Post-Bundle Patient count | 1 Patient (original, updated by PUT) | Pass |
| 6 | Individual duplicate Patient POST | 200 OK, Bundle with merged resource + info OO | Pass |
| 7 | Final Patient count | 1 Patient (no duplicates at any level) | Pass |
| 8 | MDM Golden Patient poll | Golden with HAPI-MDM tag found within 30 s | Pass |
| 9 | MDM server health | CapabilityStatement still accessible after MDM processing | Pass |

### Key findings

**Transaction dedup**: The `SERVER_INCOMING_REQUEST_PRE_HANDLED` hook handles both `CREATE` and `TRANSACTION` operations:

- **Individual POST (`CREATE`):** Merge via DAO, throw `DeduplicationMatchedException`, return Bundle with merged resource + informational `OperationOutcome` via `SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME`.
- **Transaction Bundle (`TRANSACTION`):** Iterate entries, find matching Patient/Practitioner/Organization, merge in-memory, change the entry's request from `POST` to `PUT` against the existing resource ID. The transaction processes the Bundle normally — the Patient gets updated (not duplicated) and Observations are created.

**MDM (Master Data Management)**: Built-in HAPI MDM is now enabled with PH Core identifier-only matching rules:

- Patience identifiers (PhilSys, PhilHealth) auto-match to Golden Resources via `mdm-rules.json` (host-mounted, not classpath)
- Practitioner and Organization match on any identifier system
- Subscriptions (`resthook_enabled: true`) drive async MDM processing via the internal in-memory message broker
- Golden Resources tagged `HAPI-MDM` are created asynchronously — the `PhCoreDeduplicationInterceptor` provides synchronous (instant) dedup feedback, while MDM coordinates Golden-Resource links in the background
- `MPI_LINK` table tracks source-to-Golden associations with `MATCH` result and `AUTO` link source

This two-layer design ensures instant client feedback (interceptor, sync) and canonical Golden-Resource coordination (MDM, async) without duplicate Patient, Practitioner, or Organization resources.

Generated by `tests/run-bundle-test.py` on 2026-06-17T13:37:27.965291
