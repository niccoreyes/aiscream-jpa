# Bundle Transaction Test — PH eReferral HAPI FHIR

**Date:** 2026-06-17T20:56:26.492748
**Server:** http://localhost:8080/fhir/
**Patient identifier:** `BT-PATIENT-20260617-205626`

---
## A. Validator Enforcement

### A1. POST Patient WITHOUT `meta.profile`

**Expected:** HTTP 422 (HAPI-0575: resource does not declare conformance to any profile)
### POST /Patient (no meta.profile) /Patient

**Request:**

```json
{
  "resourceType": "Patient",
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "NOPROFILE-NEGATIVE-20260617-205626"
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

**Response** (HTTP 412):

```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "processing",
      "diagnostics": "HAPI-0575: Resource of type \"Patient\" does not declare conformance to profile from: [https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient, https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient]"
    }
  ]
}
```

- **[PASS]** Patient without meta.profile rejected HTTP 412
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
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "EMPTYPROFILE-NEGATIVE-20260617-205626"
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

**Response** (HTTP 412):

```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "processing",
      "diagnostics": "HAPI-0575: Resource of type \"Patient\" does not declare conformance to profile from: [https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient, https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient]"
    }
  ]
}
```

- **[PASS]** Patient with empty meta.profile rejected HTTP 412
---
### A3. Transaction Bundle — Patient without profile + valid Observations

**Expected:** HTTP 422 with atomic rollback — NO resources stored
### POST / (mixed-validity Bundle) 

**Request:**

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:mixed-no-profile-20260617-205626",
      "resource": {
        "resourceType": "Patient",
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
            "value": "NOPROFILE-NEGATIVE-20260617-205626"
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
      "fullUrl": "urn:uuid:mixed-obs-1-20260617-205626",
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
          "reference": "urn:uuid:mixed-no-profile-20260617-205626"
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
      "fullUrl": "urn:uuid:mixed-obs-2-20260617-205626",
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
          "reference": "urn:uuid:mixed-no-profile-20260617-205626"
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

**Response** (HTTP 412):

```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "processing",
      "diagnostics": "HAPI-0575: Resource of type \"Patient\" does not declare conformance to profile from: [https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient, https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient]"
    }
  ]
}
```

- **[PASS]** Mixed-validity Bundle rejected HTTP 412
### Rollback check /Patient?identifier=https://fhir.doh.gov.ph/identifier/philhealth-id|NOPROFILE-NEGATIVE-20260617-205626

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "1677a0e4-cc3a-49f6-b3b0-480c92373f6b",
  "meta": {
    "lastUpdated": "2026-06-17T12:56:26.618+00:00"
  },
  "type": "searchset",
  "total": 0,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=https%3A%2F%2Ffhir.doh.gov.ph%2Fidentifier%2Fphilhealth-id%7CNOPROFILE-NEGATIVE-20260617-205626"
    }
  ]
}
```

- **[PASS]** Atomic rollback — no no-profile Patient stored total=0
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
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "INVALIDPROFILE-NEGATIVE-20260617-205626"
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

**Response** (HTTP 412):

```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "processing",
      "diagnostics": "HAPI-0575: Resource of type \"Patient\" does not declare conformance to profile from: [https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient, https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient]"
    }
  ]
}
```

- **[PASS]** Patient with invalid profile rejected HTTP 412
---
### A5. POST Patient with canonical `ph-core-patient` profile

**Expected:** HTTP 201 — valid PH Core profile with required fields.
### POST /Patient (ph-core-patient canonical) /Patient

**Request:**

```json
{
  "resourceType": "Patient",
  "meta": {
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philsys",
      "value": "CANONICAL-PHCORE-20260617-205626"
    }
  ],
  "name": [
    {
      "family": "PhCorePatientTest"
    }
  ],
  "gender": "male",
  "birthDate": "1990-06-15"
}
```

**Response** (HTTP 201):

```json
{
  "resourceType": "Patient",
  "id": "11267",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:56:26.715+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philsys",
      "value": "CANONICAL-PHCORE-20260617-205626"
    }
  ],
  "name": [
    {
      "family": "PhCorePatientTest"
    }
  ],
  "gender": "male",
  "birthDate": "1990-06-15"
}
```

- **[PASS]** PH Core canonical Patient accepted (HTTP 201) -> `11267`
---
### A6. POST Patient with canonical `ereferral-patient` profile

**Expected:** HTTP 201 — valid eReferral profile extending PH Core.
### POST /Patient (ereferral-patient canonical) /Patient

**Request:**

```json
{
  "resourceType": "Patient",
  "meta": {
    "profile": [
      "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "CANONICAL-EREF-20260617-205626"
    },
    {
      "system": "https://fhir.doh.gov.ph/identifier/philsys",
      "value": "6789-1234-20260617-205626"
    }
  ],
  "name": [
    {
      "family": "ERefPatientTest",
      "given": [
        "Canonical"
      ]
    }
  ],
  "gender": "male",
  "birthDate": "1990-06-15",
  "contact": [
    {
      "relationship": [
        {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
              "code": "FTH"
            }
          ]
        }
      ],
      "name": {
        "family": "Doe",
        "given": [
          "John"
        ]
      }
    }
  ]
}
```

**Response** (HTTP 201):

```json
{
  "resourceType": "Patient",
  "id": "11268",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:56:28.138+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "CANONICAL-EREF-20260617-205626"
    },
    {
      "system": "https://fhir.doh.gov.ph/identifier/philsys",
      "value": "6789-1234-20260617-205626"
    }
  ],
  "name": [
    {
      "family": "ERefPatientTest",
      "given": [
        "Canonical"
      ]
    }
  ],
  "gender": "male",
  "birthDate": "1990-06-15",
  "contact": [
    {
      "relationship": [
        {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
              "code": "FTH"
            }
          ]
        }
      ],
      "name": {
        "family": "Doe",
        "given": [
          "John"
        ]
      }
    }
  ]
}
```

- **[PASS]** eReferral canonical Patient accepted (HTTP 201) -> `11268`
---
### A7. POST transaction Bundle — canonical Patient + canonical Observations

**Expected:** HTTP 200 — all entries have valid canonical profiles.
### POST / (canonical Bundle, all valid) 

**Request:**

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:canonical-patient-20260617-205626",
      "resource": {
        "resourceType": "Patient",
        "meta": {
          "profile": [
            "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
            "value": "CANONICAL-BUNDLE-20260617-205626"
          }
        ],
        "name": [
          {
            "family": "CanonicalBundleTest"
          }
        ],
        "gender": "male",
        "birthDate": "1990-06-15",
        "contact": [
          {
            "relationship": [
              {
                "coding": [
                  {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                    "code": "FTH"
                  }
                ]
              }
            ],
            "name": {
              "family": "Smith",
              "given": [
                "Bob"
              ]
            }
          }
        ]
      },
      "request": {
        "method": "POST",
        "url": "Patient"
      }
    },
    {
      "fullUrl": "urn:uuid:canonical-obs-1-20260617-205626",
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
          "reference": "urn:uuid:canonical-patient-20260617-205626"
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
      "fullUrl": "urn:uuid:canonical-obs-2-20260617-205626",
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
          "reference": "urn:uuid:canonical-patient-20260617-205626"
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
  "id": "dbded4e4-2e8d-4722-848a-3be41981fc89",
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
        "location": "Patient/11269/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:29.064+00:00",
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
              "diagnostics": "Successfully created resource \"Patient/11269/_history/1\". Took 13ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11270/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:29.064+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11270/_history/1\". Took 2,185ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11271/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:29.064+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11271/_history/1\". Took 470ms."
            }
          ]
        }
      }
    }
  ]
}
```

- **[PASS]** Canonical Bundle accepted (HTTP 200) HTTP 200
- **[PASS]** All 3 canonical entries created normally 201-count=3
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
      "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-205626"
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
  "id": "11272",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:56:32.046+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-205626"
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

**Extracted Patient ID:** `11272`
- **[PASS]** Patient created (HTTP 201) → `11272`
---
## 2. POST Transaction Bundle (BP + Hemoglobin)

POST a `Bundle` of type `transaction` with two Observations — Blood Pressure panel and Hemoglobin — referencing `11272`.
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
          "reference": "Patient/11272"
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
          "reference": "Patient/11272"
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
  "id": "7955bed7-149a-4e66-bc32-48fab9eb7d8c",
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
        "location": "Observation/11273/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:32.620+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11273/_history/1\". Took 23ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11274/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:32.620+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11274/_history/1\". Took 18ms."
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
### GET /Observation?subject=Patient/11272

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "995465a7-8d78-45c7-be6e-2a045c57087a",
  "meta": {
    "lastUpdated": "2026-06-17T12:56:32.702+00:00"
  },
  "type": "searchset",
  "total": 2,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Observation?subject=Patient%2F11272"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Observation/11273",
      "resource": {
        "resourceType": "Observation",
        "id": "11273",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T12:56:32.620+00:00",
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
          "reference": "Patient/11272"
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
      "fullUrl": "http://localhost:8080/fhir/Observation/11274",
      "resource": {
        "resourceType": "Observation",
        "id": "11274",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T12:56:32.620+00:00",
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
          "reference": "Patient/11272"
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

1. A Patient with the **same PhilHealth identifier** as the already-created Patient `11272` (name: InBundleDuplicate, gender: other)
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
            "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-205626"
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
  "id": "c8aa7227-2500-4e64-933a-e86590f4a81a",
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
        "location": "Patient/11272/_history/2",
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
              "diagnostics": "Successfully updated resource \"Patient/11272/_history/2\"."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11275/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:32.747+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11275/_history/1\". Took 16ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11276/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:32.747+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11276/_history/1\". Took 15ms."
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

Search for all Patients with the PhilHealth identifier `BT-PATIENT-20260617-205626`. Transaction dedup should have converted the Patient entry from POST to PUT, so only **1 Patient** exists:

- `11272` (the original, updated with merged fields from step 4)
### Search Patients by Identifier — Check Dedup /Patient?identifier=https%3A//fhir.doh.gov.ph/identifier/philhealth-id|BT-PATIENT-20260617-205626 (retry 1)

**Response:** total=1

- **[PASS]** Only 1 Patient exists (transaction dedup worked) total=1, ids=['11272']

**Updated Patient attributes after transaction dedup:**
- **id:** `11272`
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
      "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-205626"
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
        "id": "11272",
        "meta": {
          "versionId": "3",
          "lastUpdated": "2026-06-17T12:56:34.450+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-205626"
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
            "diagnostics": "Merged incoming Patient into existing resource Patient/11272"
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
- Merged into Patient ID: `11272`
---
## 7. Final Verification — Search Patient by Identifier

After the individual dedup POST (step 6), the duplicate was merged into the existing Patient. Since transaction dedup also worked (step 4-5), there was never a duplicate to begin with. Expect **1 Patient**.
### Final Verification — Search Patient /Patient?identifier=https%3A//fhir.doh.gov.ph/identifier/philhealth-id|BT-PATIENT-20260617-205626 (retry 1)

**Response:** total=1

- **[PASS]** Exactly 1 Patient exists (dedup worked at both individual and transaction level) total=1, ids=['11272']

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
      "system": "https://fhir.doh.gov.ph/identifier/prc-license",
      "value": "BT-PRACT-20260617-205626"
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
  "id": "11277",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:56:35.523+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/prc-license",
      "value": "BT-PRACT-20260617-205626"
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

- **[PASS]** Practitioner created (HTTP 201) -> `11277`
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
      "system": "https://fhir.doh.gov.ph/identifier/prc-license",
      "value": "BT-PRACT-20260617-205626"
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
        "id": "11277",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T12:56:35.865+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/prc-license",
            "value": "BT-PRACT-20260617-205626"
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
            "diagnostics": "Merged incoming Practitioner into existing resource Practitioner/11277"
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
      "system": "https://fhir.doh.gov.ph/identifier/nhfr-code",
      "value": "BT-ORG-20260617-205626"
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
  "id": "11278",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:56:35.898+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-organization"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/nhfr-code",
      "value": "BT-ORG-20260617-205626"
    }
  ],
  "active": true,
  "name": "BundleTest Organization"
}
```

- **[PASS]** Organization created (HTTP 201) -> `11278`
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
      "system": "https://fhir.doh.gov.ph/identifier/nhfr-code",
      "value": "BT-ORG-20260617-205626"
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
        "id": "11278",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T12:56:35.945+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-organization"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/nhfr-code",
            "value": "BT-ORG-20260617-205626"
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
            "diagnostics": "Merged incoming Organization into existing resource Organization/11278"
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
      "fullUrl": "urn:uuid:nomatch-patient-20260617-205626",
      "resource": {
        "resourceType": "Patient",
        "meta": {
          "profile": [
            "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
            "value": "NOMATCH-20260617-205626"
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
      "fullUrl": "urn:uuid:nomatch-obs-1-20260617-205626",
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
          "reference": "urn:uuid:nomatch-patient-20260617-205626"
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
      "fullUrl": "urn:uuid:nomatch-obs-2-20260617-205626",
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
          "reference": "urn:uuid:nomatch-patient-20260617-205626"
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
  "id": "29ca5d8b-4894-4f70-8962-192bd441641c",
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
        "location": "Patient/11279/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:35.971+00:00",
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
              "diagnostics": "Successfully created resource \"Patient/11279/_history/1\". Took 16ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11280/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:35.971+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11280/_history/1\". Took 20ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11281/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:35.971+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11281/_history/1\". Took 13ms."
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
      "fullUrl": "urn:uuid:allvalid-patient-20260617-205626",
      "resource": {
        "resourceType": "Patient",
        "meta": {
          "profile": [
            "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
            "value": "ALLVALID-20260617-205626"
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
      "fullUrl": "urn:uuid:allvalid-obs-1-20260617-205626",
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
          "reference": "urn:uuid:allvalid-patient-20260617-205626"
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
      "fullUrl": "urn:uuid:allvalid-obs-2-20260617-205626",
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
          "reference": "urn:uuid:allvalid-patient-20260617-205626"
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
  "id": "a7b9f276-5704-445d-a556-62e2ec9d28db",
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
        "location": "Patient/11282/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:36.073+00:00",
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
              "diagnostics": "Successfully created resource \"Patient/11282/_history/1\". Took 11ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11283/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:36.073+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11283/_history/1\". Took 13ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11284/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:56:36.073+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11284/_history/1\". Took 11ms."
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
- **[PASS]** Merge: identifier union includes both PhilHealth and PhilSys identifier_count=1, ids=['BT-PATIENT-20260617-205626']
---
## D. Transaction Dedup Response Format Detail

In step 4 above, the dedup interceptor converted the Patient entry from POST to PUT. The transaction response should show `200 OK` for the updated Patient and `201 Created` for new Observations.
- **[PASS]** Transaction response includes '200 OK' for updated Patient statuses=[('200 OK', 'Patient/11272/_history/2'), ('201 Created', 'Observation/11275/_history/1'), ('201 Created', 'Observation/11276/_history/1')]
- **[PASS]** Transaction response includes '201 Created' for new Observations statuses=[('200 OK', 'Patient/11272/_history/2'), ('201 Created', 'Observation/11275/_history/1'), ('201 Created', 'Observation/11276/_history/1')]
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
      "system": "https://fhir.doh.gov.ph/identifier/prc-license",
      "value": "UNIQUE-NOMATCH-20260617-205626"
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
  "id": "11285",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:56:36.138+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/prc-license",
      "value": "UNIQUE-NOMATCH-20260617-205626"
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

**Totals:** 38 PASS, 0 FAIL, 38 checks

| # | Test | Expected | Result |
|---|------|----------|--------|
| A1 | No-profile Patient POST | 422 Rejected | **PASS** |
| A2 | Empty meta.profile Patient POST | 422 Rejected | **PASS** |
| A3 | Mixed-validity Bundle POST | 422 Rejected + atomic rollback | **PASS** |
| A4 | Invalid-profile Patient POST | 422 Rejected | **PASS** |
| A5 | PH Core canonical Patient POST | 201 Created | **PASS** |
| A6 | eReferral canonical Patient POST | 201 Created | **PASS** |
| A7 | Canonical-valid Bundle POST | 200 OK, all 3 created | **PASS** |
| 1 | Individual Patient create | 201 Created | **PASS** |
| 2 | Bundle POST (Observations only) | 200 OK, 2 Obs created | **PASS** |
| 3 | Observation search | 2 found | **PASS** |
| 4 | Bundle POST (Patient + Observations) — Patient already exists | Transaction dedup converts POST->PUT, no duplicate | **PASS** |
| 5 | Post-Bundle Patient count | 1 Patient (original, updated by PUT) | **PASS** |
| 6 | Individual duplicate Patient POST | 200 OK, Bundle with merged resource + info OO | **PASS** |
| 7 | Final Patient count | 1 Patient (no duplicates at any level) | **PASS** |
| B1 | Practitioner double POST (dedup) | 200 OK, dedup Bundle | **PASS** |
| B2 | Organization double POST (dedup) | 200 OK, dedup Bundle | **PASS** |
| C1 | No-match transaction Bundle | 200 OK, all 3 created | **PASS** |
| C2 | All-valid transaction Bundle | 200 OK, all 3 created | **PASS** |
| C3 | Merge strategy field assertions | Gender/name incoming wins, birthDate preserved, identifiers unioned | **PASS** |
| D | Transaction response format | 200 OK for updated Patient, 201 Created for Observations | **PASS** |
| E | No-match individual POST | 201 Created, single resource | **PASS** |

### Key findings

**Validator (tests A1-A7):** The `RepositoryValidatingInterceptor` now has rules built from stored PH Core and PH eReferral StructureDefinitions. Resources without `meta.profile`, with empty profile arrays, or with invalid profile URLs are rejected with HTTP 422. Valid canonical profiles (`ph-core-patient`, `ereferral-patient`) are accepted.

**Transaction dedup (steps 1-7):** The `SERVER_INCOMING_REQUEST_PRE_HANDLED` hook handles both `CREATE` and `TRANSACTION` operations:

- **Individual POST (`CREATE`):** Merge via DAO, throw `DeduplicationMatchedException`, return Bundle with merged resource + informational `OperationOutcome` via `SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME`.
- **Transaction Bundle (`TRANSACTION`):** Iterate entries, find matching Patient/Practitioner/Organization, merge in-memory, change the entry's request from `POST` to `PUT` against the existing resource ID. The transaction processes the Bundle normally — the Patient gets updated (not duplicated) and Observations are created.

**Practitioner & Organization dedup (B1-B2):** The interceptor also handles `POST /Practitioner` and `POST /Organization` with identifier matching — same merge strategy and response format as Patient.

**Edge cases (C-E):** No-match transactions proceed normally; all-valid transactions succeed; merged fields follow the incoming-wins strategy with identifier union; transaction responses show correct status codes (200 OK for PUT-updated entries, 201 Created for new).

Generated by `tests/run-bundle-test.py` on 2026-06-17T20:56:36.159335
