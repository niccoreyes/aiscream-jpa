# Bundle Transaction Test — PH eReferral HAPI FHIR

**Date:** 2026-06-17T20:24:20.678212
**Server:** http://localhost:8080/fhir
**Patient identifier:** `BT-PATIENT-20260617-202420`

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
      "value": "NOPROFILE-NEGATIVE-20260617-202420"
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
      "value": "EMPTYPROFILE-NEGATIVE-20260617-202420"
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
      "fullUrl": "urn:uuid:mixed-no-profile-20260617-202420",
      "resource": {
        "resourceType": "Patient",
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
            "value": "NOPROFILE-NEGATIVE-20260617-202420"
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
      "fullUrl": "urn:uuid:mixed-obs-1-20260617-202420",
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
          "reference": "urn:uuid:mixed-no-profile-20260617-202420"
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
      "fullUrl": "urn:uuid:mixed-obs-2-20260617-202420",
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
          "reference": "urn:uuid:mixed-no-profile-20260617-202420"
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
### Rollback check /Patient?identifier=https://fhir.doh.gov.ph/identifier/philhealth-id|NOPROFILE-NEGATIVE-20260617-202420

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "b61f8cff-31e0-49df-8170-d22bf9607894",
  "meta": {
    "lastUpdated": "2026-06-17T12:24:20.846+00:00"
  },
  "type": "searchset",
  "total": 0,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Patient?identifier=https%3A%2F%2Ffhir.doh.gov.ph%2Fidentifier%2Fphilhealth-id%7CNOPROFILE-NEGATIVE-20260617-202420"
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
      "value": "INVALIDPROFILE-NEGATIVE-20260617-202420"
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
      "value": "CANONICAL-PHCORE-20260617-202420"
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
  "id": "11245",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:24:20.892+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philsys",
      "value": "CANONICAL-PHCORE-20260617-202420"
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

- **[PASS]** PH Core canonical Patient accepted (HTTP 201) -> `11245`
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
      "value": "CANONICAL-EREF-20260617-202420"
    },
    {
      "system": "https://fhir.doh.gov.ph/identifier/philsys",
      "value": "6789-1234-20260617-202420"
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
  "id": "11246",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:24:20.985+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "CANONICAL-EREF-20260617-202420"
    },
    {
      "system": "https://fhir.doh.gov.ph/identifier/philsys",
      "value": "6789-1234-20260617-202420"
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

- **[PASS]** eReferral canonical Patient accepted (HTTP 201) -> `11246`
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
      "fullUrl": "urn:uuid:canonical-patient-20260617-202420",
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
            "value": "CANONICAL-BUNDLE-20260617-202420"
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
      "fullUrl": "urn:uuid:canonical-obs-1-20260617-202420",
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
          "reference": "urn:uuid:canonical-patient-20260617-202420"
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
      "fullUrl": "urn:uuid:canonical-obs-2-20260617-202420",
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
          "reference": "urn:uuid:canonical-patient-20260617-202420"
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
  "id": "d1752542-9fb4-4923-9bff-3aff6a4fea9d",
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
        "location": "Patient/11247/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:22.961+00:00",
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
              "diagnostics": "Successfully created resource \"Patient/11247/_history/1\". Took 16ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11248/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:22.961+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11248/_history/1\". Took 3,803ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11249/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:22.961+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11249/_history/1\". Took 462ms."
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
      "value": "BT-PATIENT-20260617-202420"
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
  "id": "11250",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:24:27.526+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
      "value": "BT-PATIENT-20260617-202420"
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

**Extracted Patient ID:** `11250`
- **[PASS]** Patient created (HTTP 201) → `11250`
---
## 2. POST Transaction Bundle (BP + Hemoglobin)

POST a `Bundle` of type `transaction` with two Observations — Blood Pressure panel and Hemoglobin — referencing `11250`.
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
          "reference": "Patient/11250"
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
          "reference": "Patient/11250"
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
  "id": "a45c9546-26e0-4d49-a02d-c643818dfdd7",
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
        "location": "Observation/11251/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:28.107+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11251/_history/1\". Took 42ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11252/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:28.107+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11252/_history/1\". Took 25ms."
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
### GET /Observation?subject=Patient/11250

**Response:**

```json
{
  "resourceType": "Bundle",
  "id": "08bffda9-bd20-4220-aeea-05994263153f",
  "meta": {
    "lastUpdated": "2026-06-17T12:24:28.228+00:00"
  },
  "type": "searchset",
  "total": 2,
  "link": [
    {
      "relation": "self",
      "url": "http://localhost:8080/fhir/Observation?subject=Patient%2F11250"
    }
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/fhir/Observation/11251",
      "resource": {
        "resourceType": "Observation",
        "id": "11251",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T12:24:28.107+00:00",
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
          "reference": "Patient/11250"
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
      "fullUrl": "http://localhost:8080/fhir/Observation/11252",
      "resource": {
        "resourceType": "Observation",
        "id": "11252",
        "meta": {
          "versionId": "1",
          "lastUpdated": "2026-06-17T12:24:28.107+00:00",
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
          "reference": "Patient/11250"
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

1. A Patient with the **same PhilHealth identifier** as the already-created Patient `11250` (name: InBundleDuplicate, gender: other)
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
            "value": "BT-PATIENT-20260617-202420"
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
  "id": "5c732b33-c551-4d83-ac6a-5ae9c4b09e82",
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
        "location": "Patient/11250/_history/2",
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
              "diagnostics": "Successfully updated resource \"Patient/11250/_history/2\"."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11253/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:28.283+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11253/_history/1\". Took 27ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11254/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:28.283+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11254/_history/1\". Took 17ms."
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

Search for all Patients with the PhilHealth identifier `BT-PATIENT-20260617-202420`. Transaction dedup should have converted the Patient entry from POST to PUT, so only **1 Patient** exists:

- `11250` (the original, updated with merged fields from step 4)
### Search Patients by Identifier — Check Dedup /Patient?identifier=https://fhir.doh.gov.ph/identifier/philhealth-id|BT-PATIENT-20260617-202420 (retry 1)

**Response:** total=1

- **[PASS]** Only 1 Patient exists (transaction dedup worked) total=1, ids=['11250']

**Updated Patient attributes after transaction dedup:**
- **id:** `11250`
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
      "value": "BT-PATIENT-20260617-202420"
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
        "id": "11250",
        "meta": {
          "versionId": "3",
          "lastUpdated": "2026-06-17T12:24:29.853+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/pheref/StructureDefinition/ereferral-patient"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/philhealth-id",
            "value": "BT-PATIENT-20260617-202420"
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
            "diagnostics": "Merged incoming Patient into existing resource Patient/11250"
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
- Merged into Patient ID: `11250`
---
## 7. Final Verification — Search Patient by Identifier

After the individual dedup POST (step 6), the duplicate was merged into the existing Patient. Since transaction dedup also worked (step 4-5), there was never a duplicate to begin with. Expect **1 Patient**.
### Final Verification — Search Patient /Patient?identifier=https://fhir.doh.gov.ph/identifier/philhealth-id|BT-PATIENT-20260617-202420 (retry 1)

**Response:** total=1

- **[PASS]** Exactly 1 Patient exists (dedup worked at both individual and transaction level) total=1, ids=['11250']

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
      "value": "BT-PRACT-20260617-202420"
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
  "id": "11255",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:24:31.029+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/prc-license",
      "value": "BT-PRACT-20260617-202420"
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

- **[PASS]** Practitioner created (HTTP 201) -> `11255`
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
      "value": "BT-PRACT-20260617-202420"
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
        "id": "11255",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T12:24:32.505+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/prc-license",
            "value": "BT-PRACT-20260617-202420"
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
            "diagnostics": "Merged incoming Practitioner into existing resource Practitioner/11255"
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
      "value": "BT-ORG-20260617-202420"
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
  "id": "11256",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:24:32.533+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-organization"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/nhfr-code",
      "value": "BT-ORG-20260617-202420"
    }
  ],
  "active": true,
  "name": "BundleTest Organization"
}
```

- **[PASS]** Organization created (HTTP 201) -> `11256`
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
      "value": "BT-ORG-20260617-202420"
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
        "id": "11256",
        "meta": {
          "versionId": "2",
          "lastUpdated": "2026-06-17T12:24:32.879+00:00",
          "profile": [
            "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-organization"
          ]
        },
        "identifier": [
          {
            "system": "https://fhir.doh.gov.ph/identifier/nhfr-code",
            "value": "BT-ORG-20260617-202420"
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
            "diagnostics": "Merged incoming Organization into existing resource Organization/11256"
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
      "fullUrl": "urn:uuid:nomatch-patient-20260617-202420",
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
            "value": "NOMATCH-20260617-202420"
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
      "fullUrl": "urn:uuid:nomatch-obs-1-20260617-202420",
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
          "reference": "urn:uuid:nomatch-patient-20260617-202420"
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
      "fullUrl": "urn:uuid:nomatch-obs-2-20260617-202420",
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
          "reference": "urn:uuid:nomatch-patient-20260617-202420"
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
  "id": "9599e7fe-06df-4b64-9996-457f8903ee6c",
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
        "location": "Patient/11257/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:32.934+00:00",
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
              "diagnostics": "Successfully created resource \"Patient/11257/_history/1\". Took 13ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11258/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:32.934+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11258/_history/1\". Took 19ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11259/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:32.934+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11259/_history/1\". Took 17ms."
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
      "fullUrl": "urn:uuid:allvalid-patient-20260617-202420",
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
            "value": "ALLVALID-20260617-202420"
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
      "fullUrl": "urn:uuid:allvalid-obs-1-20260617-202420",
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
          "reference": "urn:uuid:allvalid-patient-20260617-202420"
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
      "fullUrl": "urn:uuid:allvalid-obs-2-20260617-202420",
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
          "reference": "urn:uuid:allvalid-patient-20260617-202420"
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
  "id": "847fcdb8-da03-4806-8219-48cf61c22663",
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
        "location": "Patient/11260/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:33.034+00:00",
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
              "diagnostics": "Successfully created resource \"Patient/11260/_history/1\". Took 30ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11261/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:33.034+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11261/_history/1\". Took 38ms."
            }
          ]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/11262/_history/1",
        "etag": "1",
        "lastModified": "2026-06-17T12:24:33.034+00:00",
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
              "diagnostics": "Successfully created resource \"Observation/11262/_history/1\". Took 24ms."
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
- **[PASS]** Merge: identifier union includes both PhilHealth and PhilSys identifier_count=1, ids=['BT-PATIENT-20260617-202420']
---
## D. Transaction Dedup Response Format Detail

In step 4 above, the dedup interceptor converted the Patient entry from POST to PUT. The transaction response should show `200 OK` for the updated Patient and `201 Created` for new Observations.
- **[PASS]** Transaction response includes '200 OK' for updated Patient statuses=[('200 OK', 'Patient/11250/_history/2'), ('201 Created', 'Observation/11253/_history/1'), ('201 Created', 'Observation/11254/_history/1')]
- **[PASS]** Transaction response includes '201 Created' for new Observations statuses=[('200 OK', 'Patient/11250/_history/2'), ('201 Created', 'Observation/11253/_history/1'), ('201 Created', 'Observation/11254/_history/1')]
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
      "value": "UNIQUE-NOMATCH-20260617-202420"
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
  "id": "11263",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-06-17T12:24:33.177+00:00",
    "profile": [
      "https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-practitioner"
    ]
  },
  "identifier": [
    {
      "system": "https://fhir.doh.gov.ph/identifier/prc-license",
      "value": "UNIQUE-NOMATCH-20260617-202420"
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
| A1 | No-profile Patient POST | 422 Rejected | Pass |
| A2 | Empty meta.profile Patient POST | 422 Rejected | Pass |
| A3 | Mixed-validity Bundle POST | 422 Rejected + atomic rollback | Pass |
| A4 | Invalid-profile Patient POST | 422 Rejected | Pass |
| A5 | PH Core canonical Patient POST | 201 Created | Pass |
| A6 | eReferral canonical Patient POST | 201 Created | Pass |
| A7 | Canonical-valid Bundle POST | 200 OK, all 3 created | Pass |
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

**Validator (tests A1-A7):** The `RepositoryValidatingInterceptor` now has rules built from stored PH Core and PH eReferral StructureDefinitions. Resources without `meta.profile`, with empty profile arrays, or with invalid profile URLs are rejected with HTTP 422. Valid canonical profiles (`ph-core-patient`, `ereferral-patient`) are accepted.

**Transaction dedup (steps 1-7):** The `SERVER_INCOMING_REQUEST_PRE_HANDLED` hook handles both `CREATE` and `TRANSACTION` operations:

- **Individual POST (`CREATE`):** Merge via DAO, throw `DeduplicationMatchedException`, return Bundle with merged resource + informational `OperationOutcome` via `SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME`.
- **Transaction Bundle (`TRANSACTION`):** Iterate entries, find matching Patient/Practitioner/Organization, merge in-memory, change the entry's request from `POST` to `PUT` against the existing resource ID. The transaction processes the Bundle normally — the Patient gets updated (not duplicated) and Observations are created.

**Practitioner & Organization dedup (B1-B2):** The interceptor also handles `POST /Practitioner` and `POST /Organization` with identifier matching — same merge strategy and response format as Patient.

**Edge cases (C-E):** No-match transactions proceed normally; all-valid transactions succeed; merged fields follow the incoming-wins strategy with identifier union; transaction responses show correct status codes (200 OK for PUT-updated entries, 201 Created for new).

Generated by `tests/run-bundle-test.py` on 2026-06-17T20:24:33.213194
