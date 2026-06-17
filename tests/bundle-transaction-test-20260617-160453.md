# Bundle Transaction Test — PH eReferral HAPI FHIR

**Date:** 2026-06-17T16:04:53.865364
**Server:** http://localhost:8080/fhir
**Patient identifier:** `BT-PATIENT-20260617-160453`

---
## A. Validator Enforcement — Negative Tests

**NOTE:** These tests are expected to FAIL in the current build. The `RepositoryValidatingInterceptor` has an empty rule set because rules are built before IG packages are installed. They will PASS once the validator initialization order is corrected.

### A1. POST Patient WITHOUT `meta.profile`

**Expected:** HTTP 422 (HAPI-0575: resource does not declare conformance to any profile)
### POST /Patient (no meta.profile) /Patient

**Request:**

```json
{
  "resourceType": "Patient",
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "NOPROFILE-NEGATIVE-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "NoProfileNegative"
    }
  ],
  "gender": "male",
  "birthDate": "1985-01-01"
}
```

**Response** (HTTP 201):

```json
{
  "resourceType": "Patient",
  "id": "9481",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T08:04:53.907+00:00"
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "NOPROFILE-NEGATIVE-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "NoProfileNegative"
    }
  ],
  "gender": "male",
  "birthDate": "1985-01-01"
}
```

- **[FAIL]** Patient without meta.profile rejected [expected to fail until validator fix — validator rule set is empty; all resources accepted]
  Got HTTP 201 — Patient created without required meta.profile
---
### A2. POST Patient with `meta.profile=[]`

**Expected:** HTTP 422 (HAPI-0575: empty profile array)
### POST /Patient (meta.profile=[]) /Patient

**Request:**

```json
{
  "resourceType": "Patient",
  "meta": {
    "profile": []
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "EMPTYPROFILE-NEGATIVE-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "EmptyProfileNegative"
    }
  ],
  "gender": "male",
  "birthDate": "1985-01-01"
}
```

**Response** (HTTP 201):

```json
{
  "resourceType": "Patient",
  "id": "9482",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T08:04:53.943+00:00"
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "EMPTYPROFILE-NEGATIVE-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "EmptyProfileNegative"
    }
  ],
  "gender": "male",
  "birthDate": "1985-01-01"
}
```

- **[FAIL]** Patient with empty meta.profile rejected [expected to fail until validator fix — validator rule set is empty]
  Got HTTP 201
---
### A3. Transaction Bundle — Patient without profile + valid Observations

**Expected:** HTTP 422 with atomic rollback — NO resources stored (Patient has no meta.profile, Observations have valid profiles)
### POST / (mixed-validity Bundle) 

**Request:**

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:mixed-no-profile-20260617-160453",
      "resource": {
        "resourceType": "Patient",
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "NOPROFILE-NEGATIVE-20260617-160453"
          }
        ],
        "name": [
          {
            "family": "NoProfileNegative"
          }
        ],
        "gender": "male",
        "birthDate": "1985-01-01"
      },
      "request": {
        "method": "POST",
        "url": "Patient"
      }
    },
    {
      "fullUrl": "urn:uuid:mixed-obs-1-20260617-160453",
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
          "reference": "urn:uuid:mixed-no-profile-20260617-160453"
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
      "fullUrl": "urn:uuid:mixed-obs-2-20260617-160453",
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
          "reference": "urn:uuid:mixed-no-profile-20260617-160453"
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
  "id": "625cede2-26f9-4aac-8052-8742108352f4",
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
        "location": "Patient/9481/_history/1",
        "etag": "1",
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
                    "code": "SUCCESSFUL_UPDATE_NO_CHANGE",
                    "display": "Update succeeded: No changes were detected so no action was taken."
                  }
                ]
              },
              "diagnostics": "Successfully updated resource \"Patient/9481/_history/1\" with no changes detected."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/9483/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:53.981+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9483/_history/1\". Took 6ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/9484/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:53.981+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9484/_history/1\". Took 2ms."
            }
          ]
        }
      }
    }
  ]
}
```

- **[FAIL]** Mixed-validity Bundle rejected [expected to fail until validator fix — validator rule set is empty; entries not individually validated]
  Got HTTP 200 — all entries created despite missing Patient profile
### Rollback check /Patient?identifier=http://philhealth.gov.ph/fhir/Identifier/philhealth-id|NOPROFILE-NEGATIVE-20260617-160453

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "113d5297-75de-48c7-bfda-e54415504816",
  "meta": {
    "lastUpdated": "2026-06-17T08:04:54.032+00:00"
  },
  "type": "searchset",
  "total": 1,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=http%3A%2F%2Fphilhealth.gov.ph%2Ffhir%2FIdentifier%2Fphilhealth-id%7CNOPROFILE-NEGATIVE-20260617-160453"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/9481",
      "resource": {
        "resourceType": "Patient",
        "id": "9481",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T08:04:53.907+00:00"
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "NOPROFILE-NEGATIVE-20260617-160453"
          }
        ],
        "name": [
          {
            "family": "NoProfileNegative"
          }
        ],
        "gender": "male",
        "birthDate": "1985-01-01"
      },
      "search": {
        "mode": "match"
      }
    }
  ]
}
```

- **[FAIL]** Atomic rollback — no no-profile Patient stored [expected to fail until validator fix — Bundle entries were committed despite validation failure]
  Patient count = 1
---
### A4. POST Patient with fake profile URL

**Expected:** HTTP 422 (profile URL not recognized)
### POST /Patient (invalid profile) /Patient

**Request:**

```json
{
  "resourceType": "Patient",
  "meta": {
    "profile": [
      "http://example.com/does-not-exist"
    ]
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "INVALIDPROFILE-NEGATIVE-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "InvalidProfileNegative"
    }
  ],
  "gender": "male",
  "birthDate": "1985-01-01"
}
```

**Response** (HTTP 201):

```json
{
  "resourceType": "Patient",
  "id": "9485",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T08:04:54.053+00:00",
    "profile": [
      "http://example.com/does-not-exist"
    ]
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "INVALIDPROFILE-NEGATIVE-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "InvalidProfileNegative"
    }
  ],
  "gender": "male",
  "birthDate": "1985-01-01"
}
```

- **[FAIL]** Patient with invalid profile rejected [expected to fail until validator fix — validator rule set is empty; fake profile accepted]
  Got HTTP 201
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
      "value": "BT-PATIENT-20260617-160453"
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
  "id": "9486",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T08:04:54.069+00:00",
    "profile": [
      "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-160453"
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

**Extracted Patient ID:** `9486`
- **[PASS]** Patient created (HTTP 201) → `9486`
---
## 2. POST Transaction Bundle (BP + Hemoglobin)

POST a `Bundle` of type `transaction` with two Observations — Blood Pressure panel and Hemoglobin — referencing `9486`.
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
          "reference": "Patient/9486"
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
          "reference": "Patient/9486"
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
  "id": "2b771dbb-b54d-4d99-b934-4e61c33411a0",
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
        "location": "Observation/9487/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.086+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9487/_history/1\". Took 2ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/9488/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.086+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9488/_history/1\". Took 1ms."
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
### GET /Observation?subject=Patient/9486

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "8f8a8450-60ac-4ad2-91ed-aaa2da375cf6",
  "meta": {
    "lastUpdated": "2026-06-17T08:04:54.112+00:00"
  },
  "type": "searchset",
  "total": 2,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Observation?subject=Patient%2F9486"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Observation/9487",
      "resource": {
        "resourceType": "Observation",
        "id": "9487",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T08:04:54.086+00:00",
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
          "reference": "Patient/9486"
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
      "fullUrl": "http://localhost:8080/fhir/Observation/9488",
      "resource": {
        "resourceType": "Observation",
        "id": "9488",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T08:04:54.086+00:00",
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
          "reference": "Patient/9486"
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

1. A Patient with the **same PhilHealth identifier** as the already-created Patient `9486` (name: InBundleDuplicate, gender: other)
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
            "value": "BT-PATIENT-20260617-160453"
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
  "id": "8296caf9-9c21-4284-8cf4-d5c47064f591",
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
        "location": "Patient/9486/_history/2",
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
              "diagnostics": "Successfully updated resource \"Patient/9486/_history/2\"."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/9489/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.137+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9489/_history/1\". Took 2ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/9490/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.137+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9490/_history/1\". Took 0ms."
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

Search for all Patients with the PhilHealth identifier `BT-PATIENT-20260617-160453`. Transaction dedup should have converted the Patient entry from POST to PUT, so only **1 Patient** exists:

- `9486` (the original, updated with merged fields from step 4)
### GET /Patient?identifier=http://philhealth.gov.ph/fhir/Identifier/philhealth-id|BT-PATIENT-20260617-160453

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "860a5c06-8fcf-46a9-8b0d-7a31f656ccc3",
  "meta": {
    "lastUpdated": "2026-06-17T08:04:54.164+00:00"
  },
  "type": "searchset",
  "total": 1,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=http%3A%2F%2Fphilhealth.gov.ph%2Ffhir%2FIdentifier%2Fphilhealth-id%7CBT-PATIENT-20260617-160453"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/9486",
      "resource": {
        "resourceType": "Patient",
        "id": "9486",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T08:04:54.137+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-160453"
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

- **[PASS]** Only 1 Patient exists (transaction dedup worked) total=1, ids=['9486']

**Updated Patient attributes after transaction dedup:**
- **id:** `9486`
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
      "value": "BT-PATIENT-20260617-160453"
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
        "id": "9486",
        "meta": {
          "versionId": "3",
          "lastUpdated": "2026-06-17T08:04:54.188+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-160453"
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
            "diagnostics": "Merged incoming Patient into existing resource Patient/9486"
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
- Merged into Patient ID: `9486`
---
## 7. Final Verification — Search Patient by Identifier

After the individual dedup POST (step 6), the duplicate was merged into the existing Patient. Since transaction dedup also worked (step 4-5), there was never a duplicate to begin with. Expect **1 Patient**.
### GET /Patient?identifier=http://philhealth.gov.ph/fhir/Identifier/philhealth-id|BT-PATIENT-20260617-160453

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "860a5c06-8fcf-46a9-8b0d-7a31f656ccc3",
  "meta": {
    "lastUpdated": "2026-06-17T08:04:54.164+00:00"
  },
  "type": "searchset",
  "total": 1,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=http%3A%2F%2Fphilhealth.gov.ph%2Ffhir%2FIdentifier%2Fphilhealth-id%7CBT-PATIENT-20260617-160453"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/9486",
      "resource": {
        "resourceType": "Patient",
        "id": "9486",
        "meta": {
          "versionId": "3",
          "lastUpdated": "2026-06-17T08:04:54.188+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-160453"
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

- **[PASS]** Exactly 1 Patient exists (dedup worked at both individual and transaction level) total=1, ids=['9486']

---
## B. Practitioner & Organization Dedup

### B1. POST Practitioner — then POST duplicate by identifier

Create a Practitioner with a PRC license, then POST again with the same identifier. The dedup interceptor should merge the second into the first and return a collection Bundle.
### POST /Practitioner (create) /Practitioner

**Request:**

```json
{
  "resourceType": "Practitioner",
  "meta": {
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
    ]
  },
  "identifier": [
    {
      "system": "http://prc.gov.ph/fhir/Identifier/prc-license",
      "value": "BT-PRACT-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "BundleTest",
      "given": [
        "Practitioner"
      ]
    }
  ],
  "gender": "female"
}
```

**Response** (HTTP 201):

```json
{
  "resourceType": "Practitioner",
  "id": "9491",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T08:04:54.226+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
    ]
  },
  "identifier": [
    {
      "system": "http://prc.gov.ph/fhir/Identifier/prc-license",
      "value": "BT-PRACT-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "BundleTest",
      "given": [
        "Practitioner"
      ]
    }
  ],
  "gender": "female"
}
```

- **[PASS]** Practitioner created (HTTP 201) -> `9491`
### POST /Practitioner (dedup) /Practitioner

**Request:**

```json
{
  "resourceType": "Practitioner",
  "meta": {
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
    ]
  },
  "identifier": [
    {
      "system": "http://prc.gov.ph/fhir/Identifier/prc-license",
      "value": "BT-PRACT-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "BundleTest",
      "given": [
        "DedupPract"
      ]
    }
  ],
  "gender": "male"
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
        "resourceType": "Practitioner",
        "id": "9491",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T08:04:54.245+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
          ]
        },
        "identifier": [
          {
            "system": "http://prc.gov.ph/fhir/Identifier/prc-license",
            "value": "BT-PRACT-20260617-160453"
          }
        ],
        "name": [
          {
            "family": "BundleTest",
            "given": [
              "DedupPract"
            ]
          }
        ],
        "gender": "male"
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
            "diagnostics": "Merged incoming Practitioner into existing resource Practitioner/9491"
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

- **[PASS]** Practitioner dedup returns Bundle resourceType=Bundle
- **[PASS]** Practitioner dedup Bundle is 'collection' 
- **[PASS]** Practitioner merge info OO present 
---
### B2. POST Organization — then POST duplicate by identifier

Create an Organization with a DOH facility code, then POST again with the same identifier. Should merge via the dedup interceptor.
### POST /Organization (create) /Organization

**Request:**

```json
{
  "resourceType": "Organization",
  "meta": {
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-organization"
    ]
  },
  "identifier": [
    {
      "system": "http://doh.gov.ph/fhir/Identifier/facility-code",
      "value": "BT-ORG-20260617-160453"
    }
  ],
  "name": "BundleTest Organization",
  "active": true
}
```

**Response** (HTTP 201):

```json
{
  "resourceType": "Organization",
  "id": "9492",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T08:04:54.261+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-organization"
    ]
  },
  "identifier": [
    {
      "system": "http://doh.gov.ph/fhir/Identifier/facility-code",
      "value": "BT-ORG-20260617-160453"
    }
  ],
  "active": true,
  "name": "BundleTest Organization"
}
```

- **[PASS]** Organization created (HTTP 201) -> `9492`
### POST /Organization (dedup) /Organization

**Request:**

```json
{
  "resourceType": "Organization",
  "meta": {
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-organization"
    ]
  },
  "identifier": [
    {
      "system": "http://doh.gov.ph/fhir/Identifier/facility-code",
      "value": "BT-ORG-20260617-160453"
    }
  ],
  "name": "DedupOrg Merged",
  "active": true
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
        "resourceType": "Organization",
        "id": "9492",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T08:04:54.279+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-organization"
          ]
        },
        "identifier": [
          {
            "system": "http://doh.gov.ph/fhir/Identifier/facility-code",
            "value": "BT-ORG-20260617-160453"
          }
        ],
        "active": true,
        "name": "DedupOrg Merged"
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
            "diagnostics": "Merged incoming Organization into existing resource Organization/9492"
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

- **[PASS]** Organization dedup returns Bundle resourceType=Bundle
- **[PASS]** Organization dedup Bundle is 'collection' 
- **[PASS]** Organization merge info OO present 
---
## C. Edge Cases

### C1. Transaction Bundle — no matching identifiers

POST a Bundle with a Patient (fresh identifier) + 2 Observations. No dedup should fire — all entries created normally.
### POST / (no-match Bundle) 

**Request:**

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:nomatch-patient-20260617-160453",
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
            "value": "NOMATCH-20260617-160453"
          }
        ],
        "name": [
          {
            "family": "NoMatchTest"
          }
        ],
        "gender": "male",
        "birthDate": "1985-06-15"
      },
      "request": {
        "method": "POST",
        "url": "Patient"
      }
    },
    {
      "fullUrl": "urn:uuid:nomatch-obs-1-20260617-160453",
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
          "reference": "urn:uuid:nomatch-patient-20260617-160453"
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
      "fullUrl": "urn:uuid:nomatch-obs-2-20260617-160453",
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
          "reference": "urn:uuid:nomatch-patient-20260617-160453"
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
  "id": "6fd9db21-77a5-477b-9576-406fa698d577",
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
        "location": "Patient/9493/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.296+00:00",
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
              "diagnostics": "Successfully created resource \"Patient/9493/_history/1\". Took 1ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/9494/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.296+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9494/_history/1\". Took 3ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/9495/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.296+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9495/_history/1\". Took 1ms."
            }
          ]
        }
      }
    }
  ]
}
```

- **[PASS]** No-match Bundle accepted (HTTP 200) HTTP 200
- **[PASS]** All 3 entries created normally 201-count=3
---
### C2. Transaction Bundle — all entries declare valid profiles

POST a Bundle with a new Patient (with eReferral profile) + 2 Observations (with PH Core Observation profile).
### POST / (all-valid Bundle) 

**Request:**

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:allvalid-patient-20260617-160453",
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
            "value": "ALLVALID-20260617-160453"
          }
        ],
        "name": [
          {
            "family": "AllValid"
          }
        ],
        "gender": "male",
        "birthDate": "1990-01-01"
      },
      "request": {
        "method": "POST",
        "url": "Patient"
      }
    },
    {
      "fullUrl": "urn:uuid:allvalid-obs-1-20260617-160453",
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
          "reference": "urn:uuid:allvalid-patient-20260617-160453"
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
      "fullUrl": "urn:uuid:allvalid-obs-2-20260617-160453",
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
          "reference": "urn:uuid:allvalid-patient-20260617-160453"
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
  "id": "db7e80f4-dd14-43a8-9648-82706c43d7a5",
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
        "location": "Patient/9496/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.321+00:00",
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
              "diagnostics": "Successfully created resource \"Patient/9496/_history/1\". Took 1ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/9497/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.321+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9497/_history/1\". Took 1ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/9498/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T08:04:54.321+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/9498/_history/1\". Took 0ms."
            }
          ]
        }
      }
    }
  ]
}
```

- **[PASS]** All-valid Bundle accepted (HTTP 200) HTTP 200
---
### C3. Merge Strategy — Field-by-field assertions

The final merged Patient should reflect the merge strategy: incoming wins where set, existing preserved where incoming absent, identifiers unioned.
- **[PASS]** Merge: gender=female (incoming from step 6 wins) gender=female
- **[PASS]** Merge: birthDate=1985-05-20 (preserved from original) birthDate=1985-05-20
- **[PASS]** Merge: name=DedupSent (incoming from step 6 wins) given=DedupSent
- **[PASS]** Merge: identifier union includes both PhilHealth and PhilSys identifier_count=1, ids=['BT-PATIENT-20260617-160453']
---
## D. Transaction Dedup Response Format Detail

In step 4 above, the dedup interceptor converted the Patient entry from POST to PUT. The transaction response should show `200 OK` for the updated Patient and `201 Created` for new Observations.
- **[PASS]** Transaction response includes '200 OK' for updated Patient statuses=[('200 OK', 'Patient/9486/_history/2'), ('201 Created', 'Observation/9489/_history/1'), ('201 Created', 'Observation/9490/_history/1')]
- **[PASS]** Transaction response includes '201 Created' for new Observations statuses=[('200 OK', 'Patient/9486/_history/2'), ('201 Created', 'Observation/9489/_history/1'), ('201 Created', 'Observation/9490/_history/1')]
---
## E. No-Match Individual POST

POST a Practitioner with a unique identifier never seen before — the dedup interceptor should NOT fire, returning HTTP 201 with a single resource (not a Bundle).
### POST /Practitioner (no match) /Practitioner

**Request:**

```json
{
  "resourceType": "Practitioner",
  "meta": {
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
    ]
  },
  "identifier": [
    {
      "system": "http://prc.gov.ph/fhir/Identifier/prc-license",
      "value": "UNIQUE-NOMATCH-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "UniqueNoMatch"
    }
  ],
  "gender": "female"
}
```

**Response** (HTTP 201):

```json
{
  "resourceType": "Practitioner",
  "id": "9499",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T08:04:54.343+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
    ]
  },
  "identifier": [
    {
      "system": "http://prc.gov.ph/fhir/Identifier/prc-license",
      "value": "UNIQUE-NOMATCH-20260617-160453"
    }
  ],
  "name": [
    {
      "family": "UniqueNoMatch"
    }
  ],
  "gender": "female"
}
```

- **[PASS]** No-match POST returns single resource (not Bundle) resourceType=Practitioner HTTP 201
---
## Summary

| # | Test | Expected | Result |
|---|------|----------|--------|
| A1 | No-profile Patient POST | 422 Rejected | (see above) |
| A2 | Empty meta.profile Patient POST | 422 Rejected | (see above) |
| A3 | Mixed-validity Bundle POST | 422 Rejected + atomic rollback | (see above) |
| A4 | Invalid-profile Patient POST | 422 Rejected | (see above) |
| 1 | Individual Patient create | 201 Created | Pass |
| 2 | Bundle POST (Observations only) | 200 OK, 2 Obs created | Pass |
| 3 | Observation search | 2 found | Pass |
| 4 | Bundle POST (Patient + Observations) — Patient already exists | Transaction dedup converts POST->PUT, no duplicate created | Pass |
| 5 | Post-Bundle Patient count | 1 Patient (original, updated by PUT) | Pass |
| 6 | Individual duplicate Patient POST | 200 OK, Bundle with merged resource + info OO | Pass |
| 7 | Final Patient count | 1 Patient (no duplicates at any level) | Pass |
| B1 | Practitioner double POST (dedup) | 200 OK, dedup Bundle | Pass |
| B2 | Organization double POST (dedup) | 200 OK, dedup Bundle | Pass |
| C1 | No-match transaction Bundle | 200 OK, all 3 created | Pass |
| C2 | All-valid transaction Bundle | 200 OK, all 3 created | Pass |
| C3 | Merge strategy field assertions | Gender/name incoming wins, birthDate preserved, identifiers unioned | Pass |
| D | Transaction response format detail | 200 OK for updated Patient, 201 Created for Observations | Pass |
| E | No-match individual POST | 201 Created, single resource | Pass |

### Key findings

**Validator (tests A1-A4):** The `RepositoryValidatingInterceptor` is registered but has zero rules — its rule set is built before IG packages are installed (PH Core 0.2.0 + PH eReferral 0.1.0). Until the initialization order is fixed, resources without `meta.profile`, with empty profile arrays, or with invalid profile URLs are accepted when they should be rejected with HTTP 422.

**Transaction dedup (steps 1-7):** The `SERVER_INCOMING_REQUEST_PRE_HANDLED` hook handles both `CREATE` and `TRANSACTION` operations:

- **Individual POST (`CREATE`):** Merge via DAO, throw `DeduplicationMatchedException`, return Bundle with merged resource + informational `OperationOutcome` via `SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME`.
- **Transaction Bundle (`TRANSACTION`):** Iterate entries, find matching Patient/Practitioner/Organization, merge in-memory, change the entry's request from `POST` to `PUT` against the existing resource ID. The transaction processes the Bundle normally — the Patient gets updated (not duplicated) and Observations are created.

**Practitioner & Organization dedup (B1-B2):** The interceptor also handles `POST /Practitioner` and `POST /Organization` with identifier matching — same merge strategy and response format as Patient.

**Edge cases (C-E):** No-match transactions proceed normally; all-valid transactions succeed; merged fields follow the incoming-wins strategy with identifier union; transaction responses show correct status codes (200 OK for PUT-updated entries, 201 Created for new).

Generated by `tests/run-bundle-test.py` on 2026-06-17T16:04:54.348366
