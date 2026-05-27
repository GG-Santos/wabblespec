# Compliance Reference

GDPR, SOC 2, HIPAA, and PCI-DSS control requirements for spec declarations.

## GDPR

Applies when: processing personal data of EU/EEA residents, regardless of where the processor is located.

### Personal data categories

| Category | Sensitivity | Examples |
|---|---|---|
| Standard personal data | Normal | Name, email, IP address, cookie ID |
| Special category (Article 9) | High | Health, biometric, racial origin, religion, political opinion |
| Children's data | High | Any data from under-16 users (under-13 for some member states) |

### Required spec declarations

```yaml
gdpr_compliance:
  personal_data_processed:
    - type: "email address"
      purpose: "account authentication"
      legal_basis: "contract"
      retention: "duration of account + 30 days post-deletion"
    - type: "purchase history"
      purpose: "order fulfillment"
      legal_basis: "contract"
      retention: "7 years (tax obligation)"
  
  data_subject_rights:
    access: "user can download their data via Settings > Export"
    erasure: "user can delete account; data deleted within 30 days"
    portability: "export available in JSON format"
    rectification: "user can edit profile fields"
  
  data_processors:
    - name: "Stripe"
      purpose: "payment processing"
      data_shared: ["email", "billing address", "payment method"]
      dpa_in_place: true
    
  breach_notification:
    internal_sla: "identify and contain within 72 hours"
    supervisory_authority: "notify within 72 hours of discovery"
    affected_users: "notify without undue delay if high risk"
```

### Technical controls

- Encryption at rest for personal data
- Encryption in transit (TLS 1.2+)
- Pseudonymization where processing purpose allows
- Access logging for personal data stores
- Data minimization: collect only what is needed for the declared purpose

## SOC 2 (Type II)

Applies when: B2B SaaS serving enterprise customers who require SOC 2.

### Trust Service Criteria (TSC)

| TSC | Always required | Optional |
|---|---|---|
| Security (CC) | Yes | — |
| Availability (A) | No | For uptime commitments |
| Processing Integrity (PI) | No | For data processing services |
| Confidentiality (C) | No | For confidential data handling |
| Privacy (P) | No | For consumer PII |

### Security TSC — key controls spec must address

- **CC1-CC3**: organizational structure, board oversight (not applicable to spec)
- **CC4**: monitoring and risk assessment processes
- **CC5**: control activities (separation of duties, change management)
- **CC6**: logical and physical access controls — most relevant to engineering
  - MFA for all production system access
  - Role-based access control; least privilege
  - Access reviews quarterly
  - Terminated employee access revoked within 24 hours
- **CC7**: system operations (monitoring, incident response)
  - Intrusion detection
  - Vulnerability scanning
  - Incident response plan documented and tested
- **CC8**: change management
  - All changes reviewed and approved before deployment
  - Production changes via CI/CD with approval gates
- **CC9**: risk mitigation (vendor management, business continuity)

## HIPAA

Applies when: creating, receiving, maintaining, or transmitting Protected Health Information (PHI) for US healthcare context.

### PHI identifiers (any of these = PHI)

Name, geographic data smaller than state, dates (except year), phone, fax, email, SSN, medical record number, health plan beneficiary number, account number, certificate/license number, vehicle identifiers, device identifiers, URLs, IP addresses, biometric identifiers, full-face photos, any other unique identifying number.

### Required safeguards

**Technical Safeguards (required in spec):**
- Access controls: unique user identification; automatic logoff; encryption
- Audit controls: hardware, software, procedural mechanisms to record and examine access
- Integrity: protecting PHI from improper alteration or destruction
- Transmission security: encryption for PHI in transit (TLS 1.2+)

**Encryption requirements:**
- At rest: AES-256 for PHI storage
- In transit: TLS 1.2+ (TLS 1.3 preferred)
- Encryption keys: separate from encrypted data; managed keys

**Spec must declare:**
- Which fields contain PHI
- Who has access to PHI and under what conditions
- Audit log for all PHI access
- Breach notification procedure (60 days to affected individuals, HHS notification)

## PCI-DSS (Payment Card Industry)

Applies when: storing, processing, or transmitting cardholder data.

### Scope reduction (best practice)

Do not store, process, or transmit card data directly — use a payment processor (Stripe, Braintree, Square):
- Use processor's hosted payment fields (tokenization before data reaches your servers)
- Store only the token, last 4 digits, and expiry month/year
- This reduces PCI scope to SAQ A (simplest compliance level)

### If in scope (processing card data directly)

| Requirement | Control |
|---|---|
| 1 | Network segmentation — cardholder data environment isolated |
| 2 | No default passwords; harden all systems |
| 3 | Do not store sensitive authentication data after authorization |
| 4 | Encrypt cardholder data in transit |
| 5 | Anti-malware on all systems |
| 6 | Secure development practices (code review, SAST, patch management) |
| 7 | Restrict access by business need to know |
| 8 | Unique IDs + MFA for all admin access |
| 9 | Physical access controls (not applicable to cloud-only) |
| 10 | Logging and monitoring; log retention 12 months (3 months online) |
| 11 | Vulnerability scanning quarterly; penetration test annually |
| 12 | Security policy; incident response plan |

**Spec must declare:** PCI scope (in scope or out of scope via tokenization); SAQ level; compliance attestation timeline.
