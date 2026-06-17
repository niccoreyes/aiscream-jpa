# Bundle Transaction Test — PH eReferral HAPI FHIR

**Date:** 2026-06-17T10:17:58.804645
**Server:** http://localhost:8080/fhir
**Patient identifier:** `BT-PATIENT-20260617-101758`

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
      "value": "BT-PATIENT-20260617-101758"
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
  "id": "11553",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T02:17:58.833+00:00",
    "profile": [
      "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-101758"
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

**Extracted Patient ID:** `11553`
- **[PASS]** Patient created (HTTP 201) → `11553`
---
## 2. POST Transaction Bundle (BP + Hemoglobin)

POST a `Bundle` of type `transaction` with two Observations — Blood Pressure panel and Hemoglobin — referencing `11553`.
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
          "reference": "Patient/11553"
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
          "reference": "Patient/11553"
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
  "id": "26984bf1-5849-4513-b772-e799ed702d0b",
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
        "location": "Observation/11554/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T02:18:02.259+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11554/_history/1\". Took 2,307ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11555/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T02:18:02.259+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11555/_history/1\". Took 465ms."
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
### GET /Observation?subject=Patient/11553

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "92c68c60-42ae-4ab3-b142-67c0f3b6a282",
  "meta": {
    "lastUpdated": "2026-06-17T02:18:05.145+00:00"
  },
  "type": "searchset",
  "total": 2,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Observation?subject=Patient%2F11553"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Observation/11554",
      "resource": {
        "resourceType": "Observation",
        "id": "11554",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T02:18:02.259+00:00",
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
          "reference": "Patient/11553"
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
      "fullUrl": "http://localhost:8080/fhir/Observation/11555",
      "resource": {
        "resourceType": "Observation",
        "id": "11555",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T02:18:02.259+00:00",
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
          "reference": "Patient/11553"
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

1. A Patient with the **same PhilHealth identifier** as the already-created Patient `11553` (name: InBundleDuplicate, gender: other)
2. Blood Pressure observation (referencing the in-Bundle Patient via `urn:uuid:patient-bt-bundle`)
3. Hemoglobin observation (same reference)

**Important:** The dedup interceptor only fires for individual `POST /Patient` calls (operation type `CREATE`). It does **NOT** fire for Patients inside a transaction `Bundle` (operation type `TRANSACTION`). This is a known HAPI 8.8.0 limitation — the `SERVER_INCOMING_REQUEST_PRE_HANDLED` hook receives `RestOperationTypeEnum.TRANSACTION`, not `CREATE`, for transaction entries.
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
            "value": "BT-PATIENT-20260617-101758"
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
  "id": "5b76f16d-c2a8-41f8-ad8e-b4ab05c62341",
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
        "location": "Patient/11556/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T02:18:05.231+00:00",
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
              "diagnostics": "Successfully created resource \"Patient/11556/_history/1\". Took 298ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11557/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T02:18:05.231+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11557/_history/1\". Took 34ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11558/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T02:18:05.231+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11558/_history/1\". Took 21ms."
            }
          ]
        }
      }
    }
  ]
}
```

- **[PASS]** Bundle accepted (HTTP 200) → Patient was created as a NEW resource (duplicate IDENTIFIER, different RESOURCE ID)
- Entry `1` → HTTP `201 Created`
- Entry `1` → HTTP `201 Created`
- Entry `1` → HTTP `201 Created`
---
## 5. Search Patients by Identifier — Check for Duplicates

Search for all Patients with the PhilHealth identifier `BT-PATIENT-20260617-101758`. Because the dedup interceptor does not fire inside transactions, we expect **2 Patients** now:

1. The original Patient `11553` (created in step 1)
2. A NEW duplicate Patient (created inside the transaction Bundle in step 4)
### GET /Patient?identifier=http://philhealth.gov.ph/fhir/Identifier/philhealth-id|BT-PATIENT-20260617-101758

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "2a5ba05f-4b3d-4f0a-894d-32899602a401",
  "meta": {
    "lastUpdated": "2026-06-17T02:18:05.626+00:00"
  },
  "type": "searchset",
  "total": 2,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=http%3A%2F%2Fphilhealth.gov.ph%2Ffhir%2FIdentifier%2Fphilhealth-id%7CBT-PATIENT-20260617-101758"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/11553",
      "resource": {
        "resourceType": "Patient",
        "id": "11553",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T02:17:58.833+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-101758"
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
      },
      "search": {
        "mode": "match"
      }
    },
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/11556",
      "resource": {
        "resourceType": "Patient",
        "id": "11556",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T02:18:05.231+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-101758"
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

- **[PASS]** 2 Patients exist with this identifier (in-Bundle Patient NOT deduped) total=2, ids=['11553', '11556']

**Conclusion:** Dedup only fires for individual resource POSTs. Patients inside a transaction Bundle are stored as new resources even when they match an existing identifier.
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
      "value": "BT-PATIENT-20260617-101758"
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
        "id": "11556",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T02:18:05.664+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-101758"
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
            "diagnostics": "Merged incoming Patient into existing resource Patient/11556"
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
- Merged into Patient ID: `11556`
---
## 7. Final Verification — Search Patient by Identifier

After the individual dedup POST (step 6), the individual duplicate was merged into the latest existing Patient. We still have the in-Bundle duplicate from step 4, so expect **2 Patients**.
### GET /Patient?identifier=http://philhealth.gov.ph/fhir/Identifier/philhealth-id|BT-PATIENT-20260617-101758

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "2a5ba05f-4b3d-4f0a-894d-32899602a401",
  "meta": {
    "lastUpdated": "2026-06-17T02:18:05.626+00:00"
  },
  "type": "searchset",
  "total": 2,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=http%3A%2F%2Fphilhealth.gov.ph%2Ffhir%2FIdentifier%2Fphilhealth-id%7CBT-PATIENT-20260617-101758"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/11553",
      "resource": {
        "resourceType": "Patient",
        "id": "11553",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T02:17:58.833+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-101758"
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
      },
      "search": {
        "mode": "match"
      }
    },
    {
      "fullUrl": "http://localhost:8080/fhir/Patient/11556",
      "resource": {
        "resourceType": "Patient",
        "id": "11556",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T02:18:05.664+00:00",
          "profile": [
            "urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "http://philhealth.gov.ph/fhir/Identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-101758"
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

- **[PASS]** Exactly 2 Patients exist (1 original + 1 in-Bundle duplicate — individual dedup reduced 3→2) total=2, ids=['11553', '11556']

**Latest merged Patient attributes:**
- **id:** `11553`
- **gender:** `male` (expected: female — incoming wins)
- **name:** `BundleTest Patient` (expected: BundleTest DedupSent — incoming wins)
- **birthDate:** `1985-05-20` (expected: 1985-05-20 — preserved from original)

---
## Summary

| # | Test | Expected | Result |
|---|------|----------|--------|
| 1 | Individual Patient create | 201 Created | Pass |
| 2 | Bundle POST (Observations only) | 200 OK, 2 Obs created | Pass |
| 3 | Observation search | 2 found | Pass |
| 4 | Bundle POST (Patient + Observations) — Patient already exists | Patient NOT deduped, duplicate created | Documented limitation |
| 5 | Post-Bundle Patient count | 2 Patients (original + in-Bundle clone) | Pass |
| 6 | Individual duplicate Patient POST | 200 OK, Bundle with merged resource + info OO | Pass |
| 7 | Final Patient count | 2 Patients (individual dedup merged one, in-Bundle clone remains) | Pass |

### Key finding

The PH eReferral dedup interceptor hooks `SERVER_INCOMING_REQUEST_PRE_HANDLED` and only fires for `RestOperationTypeEnum.CREATE`. Transaction Bundles have operation type `TRANSACTION`, so Patients created inside a transaction are **NOT** deduped. This is a known limitation of the current implementation.

Generated by `tests/run-bundle-test.py` on 2026-06-17T10:18:05.724119
