"""
Example usage of the AI Guardrail System
Demonstrates PHI detection, redaction, access control, and compliance enforcement
"""

from ai_guardrail_system import (
    AIGuardrail, ComplianceLevel, AccessLevel
)


def example_basic_phi_detection():
    """Example 1: Basic PHI Detection"""
    print("\n" + "="*70)
    print("EXAMPLE 1: BASIC PHI DETECTION")
    print("="*70)
    
    guardrail = AIGuardrail(ComplianceLevel.MODERATE)
    guardrail.register_user("clinician1", AccessLevel.CLINICIAN)
    
    test_text = """
    Patient Information:
    Name: John Doe
    SSN: 123-45-6789
    DOB: 01/15/1980
    Phone: (555) 123-4567
    Email: john.doe@example.com
    MRN: 987654
    Insurance ID: INS-123456789
    """
    
    result = guardrail.process_request("clinician1", test_text, "read")
    
    print(f"\nPHI Detected: {result['phi_detected']}")
    print(f"Number of PHI Entities: {result['phi_count']}")
    print(f"Action Taken: {result['action_taken']}")
    print(f"\nDetected Entities:")
    for entity in result['phi_entities']:
        print(f"  - {entity['type']}: {entity['value']} (confidence: {entity['confidence']})")


def example_access_control():
    """Example 2: Access Control and Redaction"""
    print("\n" + "="*70)
    print("EXAMPLE 2: ACCESS CONTROL AND REDACTION")
    print("="*70)
    
    guardrail = AIGuardrail(ComplianceLevel.MODERATE)
    
    # Register users with different access levels
    guardrail.register_user("clinician1", AccessLevel.CLINICIAN)
    guardrail.register_user("researcher1", AccessLevel.RESEARCHER)
    guardrail.register_user("admin1", AccessLevel.ADMIN)
    
    test_text = """
    Patient: Jane Smith
    SSN: 987-65-4321
    DOB: 05/20/1975
    Phone: (555) 987-6543
    Email: jane.smith@example.com
    MRN: 654321
    """
    
    # Clinician can view PHI
    print("\n--- CLINICIAN ACCESS (Can view PHI) ---")
    result = guardrail.process_request("clinician1", test_text, "read")
    print(f"Success: {result['success']}")
    print(f"Action: {result['action_taken']}")
    print(f"Processed Text:\n{result['processed_text']}")
    
    # Researcher cannot view PHI (gets redacted)
    print("\n--- RESEARCHER ACCESS (Cannot view PHI - Redacted) ---")
    result = guardrail.process_request("researcher1", test_text, "read")
    print(f"Success: {result['success']}")
    print(f"Action: {result['action_taken']}")
    print(f"Processed Text:\n{result['processed_text']}")
    
    # Admin can view PHI
    print("\n--- ADMIN ACCESS (Can view PHI) ---")
    result = guardrail.process_request("admin1", test_text, "read")
    print(f"Success: {result['success']}")
    print(f"Action: {result['action_taken']}")


def example_compliance_levels():
    """Example 3: Different Compliance Levels"""
    print("\n" + "="*70)
    print("EXAMPLE 3: COMPLIANCE LEVELS")
    print("="*70)
    
    test_text = """
    Patient ID: PID-123456
    SSN: 111-22-3333
    Insurance: INS-987654321
    """
    
    # STRICT mode
    print("\n--- STRICT MODE (Block all PHI access for non-authorized users) ---")
    guardrail_strict = AIGuardrail(ComplianceLevel.STRICT)
    guardrail_strict.register_user("guest1", AccessLevel.GUEST)
    result = guardrail_strict.process_request("guest1", test_text, "read")
    print(f"Success: {result['success']}")
    print(f"Action: {result['action_taken']}")
    
    # MODERATE mode
    print("\n--- MODERATE MODE (Redact PHI for non-authorized users) ---")
    guardrail_moderate = AIGuardrail(ComplianceLevel.MODERATE)
    guardrail_moderate.register_user("guest1", AccessLevel.GUEST)
    result = guardrail_moderate.process_request("guest1", test_text, "read")
    print(f"Success: {result['success']}")
    print(f"Action: {result['action_taken']}")
    print(f"Processed Text:\n{result['processed_text']}")
    
    # PERMISSIVE mode
    print("\n--- PERMISSIVE MODE (Allow all, log only) ---")
    guardrail_permissive = AIGuardrail(ComplianceLevel.PERMISSIVE)
    guardrail_permissive.register_user("guest1", AccessLevel.GUEST)
    result = guardrail_permissive.process_request("guest1", test_text, "read")
    print(f"Success: {result['success']}")
    print(f"Action: {result['action_taken']}")


def example_audit_trail():
    """Example 4: Audit Trail and Compliance Logging"""
    print("\n" + "="*70)
    print("EXAMPLE 4: AUDIT TRAIL AND COMPLIANCE LOGGING")
    print("="*70)
    
    guardrail = AIGuardrail(ComplianceLevel.MODERATE)
    guardrail.register_user("user1", AccessLevel.CLINICIAN)
    guardrail.register_user("user2", AccessLevel.RESEARCHER)
    
    test_texts = [
        "Patient SSN: 123-45-6789",
        "Email: test@example.com",
        "Phone: (555) 123-4567"
    ]
    
    # Process multiple requests
    for i, text in enumerate(test_texts):
        guardrail.process_request("user1", text, "read")
        guardrail.process_request("user2", text, "read")
    
    # Get audit trail
    print("\n--- FULL AUDIT TRAIL ---")
    audit = guardrail.get_audit_trail()
    for log in audit:
        print(f"\nTimestamp: {log['timestamp']}")
        print(f"User: {log['user_id']} (Level: {log['access_level']})")
        print(f"Action: {log['action']}")
        print(f"PHI Detected: {log['phi_detected']} ({log['phi_count']} entities)")
        print(f"Status: {log['status']}")
    
    # Get audit trail for specific user
    print("\n--- AUDIT TRAIL FOR user1 ---")
    audit_user1 = guardrail.get_audit_trail("user1")
    print(f"Total accesses: {len(audit_user1)}")
    for log in audit_user1:
        print(f"  {log['timestamp']} - {log['action']} - {log['status']}")


def example_phi_types():
    """Example 5: Different PHI Types Detection"""
    print("\n" + "="*70)
    print("EXAMPLE 5: DIFFERENT PHI TYPES DETECTION")
    print("="*70)
    
    guardrail = AIGuardrail(ComplianceLevel.MODERATE)
    guardrail.register_user("admin1", AccessLevel.ADMIN)
    
    test_text = """
    Medical Record:
    SSN: 555-66-7777
    MRN: 123456
    Patient ID: PID-ABC123
    DOB: 12/25/1990
    Phone: (555) 555-5555
    Email: patient@hospital.com
    Insurance ID: INS-XYZ789
    Hospital ID: HOSP-001
    Prescription: Rx-MED123456
    Credit Card: 4532-1234-5678-9012
    IP Address: 192.168.1.100
    """
    
    result = guardrail.process_request("admin1", test_text, "read")
    
    print(f"\nTotal PHI Entities Detected: {result['phi_count']}")
    print("\nDetailed Entity Information:")
    
    entity_types = {}
    for entity in result['phi_entities']:
        entity_type = entity['type']
        if entity_type not in entity_types:
            entity_types[entity_type] = []
        entity_types[entity_type].append(entity)
    
    for entity_type, entities in sorted(entity_types.items()):
        print(f"\n{entity_type.upper()}:")
        for entity in entities:
            print(f"  - Value: {entity['value']}")
            print(f"    Position: {entity['position']}")
            print(f"    Confidence: {entity['confidence']}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("AI GUARDRAIL SYSTEM - COMPREHENSIVE EXAMPLES")
    print("="*70)
    
    example_basic_phi_detection()
    example_access_control()
    example_compliance_levels()
    example_audit_trail()
    example_phi_types()
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
