# AI Guardrail System - Complete Documentation

## Overview

The AI Guardrail System is a comprehensive solution for protecting Protected Health Information (PHI) in healthcare applications. It provides automatic PHI detection, redaction, access control, and compliance enforcement with HIPAA standards.

## Features

### 1. **Automatic PHI Detection**
- Detects 11 types of PHI patterns:
  - Social Security Numbers (SSN)
  - Medical Record Numbers (MRN)
  - Phone Numbers
  - Email Addresses
  - Dates of Birth
  - Patient IDs
  - Insurance IDs
  - Credit Card Numbers
  - IP Addresses
  - Hospital IDs
  - Prescription Numbers

### 2. **Automatic Redaction**
- Full redaction: Replaces PHI with [TYPE] placeholders
- Partial redaction: Shows first/last N characters with asterisks
- Configurable redaction strategies

### 3. **Access Control**
- Role-based access control (RBAC)
- 5 access levels:
  - **ADMIN**: Full access to all data and controls
  - **CLINICIAN**: Can view PHI, limited controls
  - **RESEARCHER**: Cannot view PHI, can export redacted data
  - **PATIENT**: Can view own data only
  - **GUEST**: Minimal access, no PHI viewing

### 4. **Compliance Enforcement**
- 3 compliance levels:
  - **STRICT**: Block all PHI access for unauthorized users
  - **MODERATE**: Redact PHI for unauthorized users (default)
  - **PERMISSIVE**: Allow all access, log only

### 5. **Access Monitoring**
- Comprehensive audit logging
- Tracks all access events with:
  - User ID and access level
  - Timestamp
  - Action performed
  - PHI detection status
  - Access status (allowed/blocked/redacted)
- Audit trail retrieval by user or globally

## Architecture

### Core Components

#### 1. PHIDetector
Detects PHI entities using regex patterns.

```python
detector = PHIDetector()
entities = detector.detect(text)
```

#### 2. PHIRedactor
Redacts detected PHI from text.

```python
redactor = PHIRedactor()
redacted_text, count = redactor.redact(text, entities)
```

#### 3. AccessControl
Manages user roles and permissions.

```python
access_control = AccessControl()
access_control.register_user("user1", AccessLevel.CLINICIAN)
has_permission = access_control.has_permission("user1", "view_phi")
```

#### 4. ComplianceEnforcer
Enforces compliance policies based on user access level.

```python
enforcer = ComplianceEnforcer(ComplianceLevel.MODERATE)
processed_text, allowed, action = enforcer.enforce(
    user_id, text, access_control, phi_entities
)
```

#### 5. AIGuardrail
Main orchestrator combining all components.

```python
guardrail = AIGuardrail(ComplianceLevel.MODERATE)
result = guardrail.process_request(user_id, text, action)
```

## Usage Examples

### Basic Setup

```python
from ai_guardrail_system import AIGuardrail, ComplianceLevel, AccessLevel

# Initialize guardrail
guardrail = AIGuardrail(ComplianceLevel.MODERATE)

# Register users
guardrail.register_user("clinician1", AccessLevel.CLINICIAN)
guardrail.register_user("researcher1", AccessLevel.RESEARCHER)
```

### Process Request

```python
text = """
Patient: John Doe
SSN: 123-45-6789
DOB: 01/15/1980
Phone: (555) 123-4567
"""

result = guardrail.process_request("clinician1", text, "read")

print(f"Success: {result['success']}")
print(f"PHI Detected: {result['phi_detected']}")
print(f"PHI Count: {result['phi_count']}")
print(f"Action: {result['action_taken']}")
print(f"Processed Text: {result['processed_text']}")
```

### Access Control Example

```python
# Clinician can view PHI
result_clinician = guardrail.process_request("clinician1", text, "read")
# Result: action_taken = "allowed_with_phi"

# Researcher cannot view PHI (gets redacted)
result_researcher = guardrail.process_request("researcher1", text, "read")
# Result: action_taken = "redacted"
# Processed text has PHI replaced with [TYPE]
```

### Audit Trail

```python
# Get all audit logs
audit_trail = guardrail.get_audit_trail()

# Get audit logs for specific user
user_audit = guardrail.get_audit_trail("clinician1")

for log in audit_trail:
    print(f"{log['timestamp']} - {log['user_id']} - {log['status']}")
```

## Compliance Levels

### STRICT Mode
- Blocks all PHI access for unauthorized users
- Returns error if PHI detected and user lacks permission
- Use case: Highly sensitive environments

```python
guardrail = AIGuardrail(ComplianceLevel.STRICT)
```

### MODERATE Mode (Default)
- Redacts PHI for unauthorized users
- Allows access with redacted content
- Logs all access events
- Use case: Standard healthcare environments

```python
guardrail = AIGuardrail(ComplianceLevel.MODERATE)
```

### PERMISSIVE Mode
- Allows all access
- Logs all events for audit
- No redaction
- Use case: Development/testing environments

```python
guardrail = AIGuardrail(ComplianceLevel.PERMISSIVE)
```

## Access Levels and Permissions

| Permission | Admin | Clinician | Researcher | Patient | Guest |
|-----------|-------|-----------|-----------|---------|-------|
| view_phi | ✓ | ✓ | ✗ | ✓ | ✗ |
| redact_phi | ✓ | ✗ | ✗ | ✗ | ✗ |
| view_logs | ✓ | ✗ | ✗ | ✗ | ✗ |
| modify_policies | ✓ | ✗ | ✗ | ✗ | ✗ |
| export_data | ✓ | ✗ | ✓ | ✗ | ✗ |

## PHI Detection Patterns

### Supported PHI Types

1. **SSN**: `123-45-6789`
2. **Medical Record**: `MRN: 987654`
3. **Phone**: `(555) 123-4567`
4. **Email**: `user@example.com`
5. **Date of Birth**: `01/15/1980`
6. **Patient ID**: `PID-123456`
7. **Insurance ID**: `INS-123456789`
8. **Credit Card**: `4532-1234-5678-9012`
9. **IP Address**: `192.168.1.100`
10. **Hospital ID**: `HOSP-001`
11. **Prescription**: `Rx-MED123456`

## Response Format

### Process Request Response

```python
{
    'success': bool,                    # Request allowed/processed
    'processed_text': str,              # Text after processing
    'phi_detected': bool,               # PHI found in text
    'phi_count': int,                   # Number of PHI entities
    'phi_entities': [                   # Detected entities
        {
            'type': str,                # Entity type
            'value': str,               # Entity value
            'position': tuple,          # (start, end) position
            'confidence': float         # Detection confidence
        }
    ],
    'action_taken': str,                # Action performed
    'message': str                      # Status message
}
```

### Audit Log Entry

```python
{
    'user_id': str,                     # User identifier
    'access_level': str,                # User's access level
    'timestamp': str,                   # ISO format timestamp
    'action': str,                      # Action performed
    'resource': str,                    # Resource accessed
    'phi_detected': bool,               # PHI found
    'phi_count': int,                   # Number of PHI entities
    'status': str,                      # allowed/blocked/redacted
    'details': str                      # Additional details
}
```

## Integration Guide

### With Flask API

```python
from flask import Flask, request, jsonify
from ai_guardrail_system import AIGuardrail, AccessLevel

app = Flask(__name__)
guardrail = AIGuardrail()

@app.route('/api/process', methods=['POST'])
def process_text():
    data = request.json
    user_id = data.get('user_id')
    text = data.get('text')
    
    result = guardrail.process_request(user_id, text, "read")
    return jsonify(result)

@app.route('/api/audit', methods=['GET'])
def get_audit():
    user_id = request.args.get('user_id')
    audit = guardrail.get_audit_trail(user_id)
    return jsonify(audit)
```

### With FastAPI

```python
from fastapi import FastAPI
from ai_guardrail_system import AIGuardrail

app = FastAPI()
guardrail = AIGuardrail()

@app.post("/process")
async def process_text(user_id: str, text: str):
    result = guardrail.process_request(user_id, text, "read")
    return result

@app.get("/audit")
async def get_audit(user_id: str = None):
    audit = guardrail.get_audit_trail(user_id)
    return audit
```

## Security Considerations

1. **User Registration**: Always register users with appropriate access levels
2. **Compliance Level**: Choose appropriate compliance level for your environment
3. **Audit Logging**: Regularly review audit trails for suspicious activity
4. **Pattern Updates**: Keep PHI detection patterns updated with new formats
5. **Access Control**: Implement additional authentication/authorization layers
6. **Data Storage**: Ensure audit logs are securely stored and encrypted

## Performance Considerations

- PHI detection uses compiled regex patterns for efficiency
- Redaction is O(n) where n is number of detected entities
- Audit logging is asynchronous and non-blocking
- Suitable for real-time processing of healthcare data

## Limitations

1. Regex-based detection may have false positives/negatives
2. Does not detect context-based PHI (e.g., "the patient" without name)
3. Limited to English language patterns
4. Does not handle encrypted or obfuscated PHI
5. Requires explicit user registration

## Future Enhancements

- Machine learning-based PHI detection
- Multi-language support
- Custom pattern registration
- Advanced anomaly detection
- Integration with HIPAA audit requirements
- Real-time compliance reporting

## Support and Troubleshooting

### Issue: PHI not detected
- Check if pattern matches the expected format
- Verify regex patterns are correct
- Consider adding custom patterns

### Issue: False positives
- Review detected entities
- Adjust confidence thresholds
- Implement custom validation

### Issue: Performance degradation
- Check audit log size
- Implement log rotation
- Optimize pattern matching

## License

This system is designed for healthcare compliance and should be used in accordance with HIPAA regulations and local healthcare data protection laws.

## References

- HIPAA Privacy Rule: https://www.hhs.gov/hipaa/for-professionals/privacy/
- PHI Definition: https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/
- HIPAA Security Rule: https://www.hhs.gov/hipaa/for-professionals/security/
