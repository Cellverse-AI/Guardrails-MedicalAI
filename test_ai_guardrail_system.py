"""
Unit Tests for AI Guardrail System
Tests PHI detection, redaction, access control, and compliance enforcement
"""

import unittest
import sys
import os

#sys.path.insert(0, os.path.expanduser(''))

from ai_guardrail_system import (
    PHIDetector, PHIRedactor, AccessControl, ComplianceEnforcer,
    AIGuardrail, PHIEntity, AccessLog, ComplianceLevel, AccessLevel
)


class TestPHIDetector(unittest.TestCase):
    """Test PHI detection functionality"""
    
    def setUp(self):
        self.detector = PHIDetector()
    
    def test_detect_ssn(self):
        """Test SSN detection"""
        text = "Patient SSN is 123-45-6789"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, 'ssn')
        self.assertEqual(entities[0].value, '123-45-6789')
        self.assertEqual(entities[0].redacted_value, '[SSN]')
    
    def test_detect_medical_record(self):
        """Test medical record number detection"""
        text = "MRN: 1234567"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, 'medical_record')
        self.assertIn('1234567', entities[0].value)
    
    def test_detect_phone(self):
        """Test phone number detection"""
        test_cases = [
            "Call 555-123-4567",
            "Phone: (555) 123-4567",
            "Contact: 555.123.4567"
        ]
        for text in test_cases:
            entities = self.detector.detect(text)
            self.assertGreater(len(entities), 0, f"Failed to detect phone in: {text}")
            self.assertEqual(entities[0].entity_type, 'phone')
    
    def test_detect_email(self):
        """Test email detection"""
        text = "Contact: patient@hospital.com"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, 'email')
        self.assertEqual(entities[0].value, 'patient@hospital.com')
    
    def test_detect_date_of_birth(self):
        """Test date of birth detection"""
        text = "DOB: 12/31/1990"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, 'date_of_birth')
        self.assertEqual(entities[0].value, '12/31/1990')
    
    def test_detect_patient_id(self):
        """Test patient ID detection"""
        text = "Patient ID: ABC123456"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, 'patient_id')
        self.assertIn('ABC123456', entities[0].value)
    
    def test_detect_multiple_phi(self):
        """Test detection of multiple PHI entities"""
        text = "Patient SSN: 123-45-6789, Phone: 555-123-4567, Email: test@example.com"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 3)
        entity_types = [e.entity_type for e in entities]
        self.assertIn('ssn', entity_types)
        self.assertIn('phone', entity_types)
        self.assertIn('email', entity_types)
    
    def test_detect_no_phi(self):
        """Test text with no PHI"""
        text = "This is a normal text without any PHI"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 0)
    
    def test_entity_positions(self):
        """Test that entity positions are correct"""
        text = "SSN: 123-45-6789 and email: test@example.com"
        entities = self.detector.detect(text)
        for entity in entities:
            extracted = text[entity.start_pos:entity.end_pos]
            self.assertEqual(extracted, entity.value)
    
    def test_detect_insurance_id(self):
        """Test insurance ID detection"""
        text = "Insurance ID: ABC12345678"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, 'insurance_id')
    
    def test_detect_credit_card(self):
        """Test credit card detection"""
        text = "Card: 1234-5678-9012-3456"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, 'credit_card')


class TestPHIRedactor(unittest.TestCase):
    """Test PHI redaction functionality"""
    
    def setUp(self):
        self.detector = PHIDetector()
        self.redactor = PHIRedactor()
    
    def test_full_redaction(self):
        """Test full redaction of PHI"""
        text = "Patient SSN is 123-45-6789"
        entities = self.detector.detect(text)
        redacted_text, count = self.redactor.redact(text, entities)
        self.assertEqual(count, 1)
        self.assertNotIn('123-45-6789', redacted_text)
        self.assertIn('[SSN]', redacted_text)
    
    def test_multiple_redactions(self):
        """Test redaction of multiple PHI entities"""
        text = "SSN: 123-45-6789, Phone: 555-123-4567"
        entities = self.detector.detect(text)
        redacted_text, count = self.redactor.redact(text, entities)
        self.assertEqual(count, 2)
        self.assertNotIn('123-45-6789', redacted_text)
        self.assertNotIn('555-123-4567', redacted_text)
    
    def test_partial_redaction(self):
        """Test partial redaction"""
        text = "SSN: 123-45-6789"
        entities = self.detector.detect(text)
        redacted_text = self.redactor.partial_redact(text, entities, show_chars=2)
        self.assertIn('12', redacted_text)
        self.assertIn('89', redacted_text)
        self.assertIn('*', redacted_text)
    
    def test_no_entities_redaction(self):
        """Test redaction with no entities"""
        text = "Normal text"
        redacted_text, count = self.redactor.redact(text, [])
        self.assertEqual(text, redacted_text)
        self.assertEqual(count, 0)
    
    def test_redaction_preserves_text_structure(self):
        """Test that redaction preserves surrounding text"""
        text = "Patient name is John, SSN: 123-45-6789, lives in NYC"
        entities = self.detector.detect(text)
        redacted_text, count = self.redactor.redact(text, entities)
        self.assertIn('Patient name is John', redacted_text)
        self.assertIn('lives in NYC', redacted_text)
    
    def test_partial_redaction_short_value(self):
        """Test partial redaction with short values"""
        text = "ID: AB"
        entity = PHIEntity(
            entity_type='test',
            value='AB',
            start_pos=4,
            end_pos=6,
            confidence=0.95,
            redacted_value='[TEST]'
        )
        redacted_text = self.redactor.partial_redact(text, [entity], show_chars=2)
        self.assertIn('*', redacted_text)


class TestAccessControl(unittest.TestCase):
    """Test access control functionality"""
    
    def setUp(self):
        self.access_control = AccessControl()
    
    def test_register_user(self):
        """Test user registration"""
        self.access_control.register_user("user1", AccessLevel.CLINICIAN)
        level = self.access_control.get_access_level("user1")
        self.assertEqual(level, AccessLevel.CLINICIAN)
    
    def test_admin_permissions(self):
        """Test admin has all permissions"""
        self.access_control.register_user("admin1", AccessLevel.ADMIN)
        self.assertTrue(self.access_control.has_permission("admin1", "view_phi"))
        self.assertTrue(self.access_control.has_permission("admin1", "redact_phi"))
        self.assertTrue(self.access_control.has_permission("admin1", "view_logs"))
        self.assertTrue(self.access_control.has_permission("admin1", "modify_policies"))
        self.assertTrue(self.access_control.has_permission("admin1", "export_data"))
    
    def test_clinician_permissions(self):
        """Test clinician permissions"""
        self.access_control.register_user("doc1", AccessLevel.CLINICIAN)
        self.assertTrue(self.access_control.has_permission("doc1", "view_phi"))
        self.assertFalse(self.access_control.has_permission("doc1", "modify_policies"))
    
    def test_researcher_permissions(self):
        """Test researcher permissions"""
        self.access_control.register_user("researcher1", AccessLevel.RESEARCHER)
        self.assertFalse(self.access_control.has_permission("researcher1", "view_phi"))
        self.assertTrue(self.access_control.has_permission("researcher1", "export_data"))
    
    def test_patient_permissions(self):
        """Test patient permissions"""
        self.access_control.register_user("patient1", AccessLevel.PATIENT)
        self.assertTrue(self.access_control.has_permission("patient1", "view_phi"))
        self.assertFalse(self.access_control.has_permission("patient1", "export_data"))
    
    def test_guest_permissions(self):
        """Test guest has no permissions"""
        self.access_control.register_user("guest1", AccessLevel.GUEST)
        self.assertFalse(self.access_control.has_permission("guest1", "view_phi"))
        self.assertFalse(self.access_control.has_permission("guest1", "export_data"))
    
    def test_unregistered_user(self):
        """Test unregistered user has no permissions"""
        self.assertFalse(self.access_control.has_permission("unknown", "view_phi"))
        self.assertIsNone(self.access_control.get_access_level("unknown"))
    
    def test_multiple_users(self):
        """Test multiple user registrations"""
        self.access_control.register_user("admin1", AccessLevel.ADMIN)
        self.access_control.register_user("doc1", AccessLevel.CLINICIAN)
        self.access_control.register_user("researcher1", AccessLevel.RESEARCHER)
        
        self.assertEqual(self.access_control.get_access_level("admin1"), AccessLevel.ADMIN)
        self.assertEqual(self.access_control.get_access_level("doc1"), AccessLevel.CLINICIAN)
        self.assertEqual(self.access_control.get_access_level("researcher1"), AccessLevel.RESEARCHER)


class TestComplianceEnforcer(unittest.TestCase):
    """Test compliance enforcement functionality"""
    
    def setUp(self):
        self.access_control = AccessControl()
        self.detector = PHIDetector()
    
    def test_strict_mode_blocks_unauthorized_phi(self):
        """Test strict mode blocks PHI for unauthorized users"""
        enforcer = ComplianceEnforcer(ComplianceLevel.STRICT)
        self.access_control.register_user("researcher1", AccessLevel.RESEARCHER)
        
        text = "SSN: 123-45-6789"
        entities = self.detector.detect(text)
        
        result_text, allowed, message = enforcer.enforce(
            "researcher1", text, self.access_control, entities
        )
        self.assertFalse(allowed)
        self.assertEqual(message, "PHI access denied")
    
    def test_strict_mode_allows_authorized_phi(self):
        """Test strict mode allows PHI for authorized users"""
        enforcer = ComplianceEnforcer(ComplianceLevel.STRICT)
        self.access_control.register_user("doc1", AccessLevel.CLINICIAN)
        
        text = "SSN: 123-45-6789"
        entities = self.detector.detect(text)
        
        result_text, allowed, message = enforcer.enforce(
            "doc1", text, self.access_control, entities
        )
        self.assertTrue(allowed)
        self.assertEqual(message, "allowed")
    
    def test_moderate_mode_redacts_phi(self):
        """Test moderate mode redacts PHI for unauthorized users"""
        enforcer = ComplianceEnforcer(ComplianceLevel.MODERATE)
        self.access_control.register_user("researcher1", AccessLevel.RESEARCHER)
        
        text = "SSN: 123-45-6789"
        entities = self.detector.detect(text)
        
        result_text, allowed, message = enforcer.enforce(
            "researcher1", text, self.access_control, entities
        )
        self.assertTrue(allowed)
        self.assertEqual(message, "redacted")
        self.assertNotIn('123-45-6789', result_text)
    
    def test_permissive_mode_allows_all(self):
        """Test permissive mode allows all access"""
        enforcer = ComplianceEnforcer(ComplianceLevel.PERMISSIVE)
        self.access_control.register_user("guest1", AccessLevel.GUEST)
        
        text = "SSN: 123-45-6789"
        entities = self.detector.detect(text)
        
        result_text, allowed, message = enforcer.enforce(
            "guest1", text, self.access_control, entities
        )
        self.assertTrue(allowed)
        self.assertEqual(message, "allowed")
    
    def test_access_logging(self):
        """Test access logging functionality"""
        enforcer = ComplianceEnforcer(ComplianceLevel.MODERATE)
        
        enforcer.log_access(
            user_id="user1",
            access_level="clinician",
            action="read",
            resource="patient_record",
            phi_detected=True,
            phi_count=2,
            status="allowed",
            details="PHI viewed"
        )
        
        logs = enforcer.get_audit_trail()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['user_id'], 'user1')
        self.assertEqual(logs[0]['phi_count'], 2)
    
    def test_audit_trail_filtering(self):
        """Test audit trail filtering by user"""
        enforcer = ComplianceEnforcer(ComplianceLevel.MODERATE)
        
        enforcer.log_access("user1", "admin", "read", "data", True, 1, "allowed")
        enforcer.log_access("user2", "clinician", "write", "data", False, 0, "allowed")
        enforcer.log_access("user1", "admin", "delete", "data", False, 0, "blocked")
        
        user1_logs = enforcer.get_audit_trail(user_id="user1")
        self.assertEqual(len(user1_logs), 2)
        
        all_logs = enforcer.get_audit_trail()
        self.assertEqual(len(all_logs), 3)


class TestAIGuardrail(unittest.TestCase):
    """Test complete AI Guardrail system"""
    
    def setUp(self):
        self.guardrail = AIGuardrail(ComplianceLevel.MODERATE)
    
    def test_process_request_with_phi_authorized(self):
        """Test processing request with PHI for authorized user"""
        self.guardrail.register_user("doc1", AccessLevel.CLINICIAN)
        
        text = "Patient SSN: 123-45-6789"
        result = self.guardrail.process_request("doc1", text, "read")
        
        self.assertTrue(result['success'])
        self.assertTrue(result['phi_detected'])
        self.assertEqual(result['phi_count'], 1)
        self.assertIn('123-45-6789', result['processed_text'])
    
    def test_process_request_with_phi_unauthorized(self):
        """Test processing request with PHI for unauthorized user"""
        self.guardrail.register_user("researcher1", AccessLevel.RESEARCHER)
        
        text = "Patient SSN: 123-45-6789"
        result = self.guardrail.process_request("researcher1", text, "read")
        
        self.assertTrue(result['success'])
        self.assertTrue(result['phi_detected'])
        self.assertEqual(result['phi_count'], 1)
        self.assertNotIn('123-45-6789', result['processed_text'])
        self.assertEqual(result['action_taken'], 'redacted')
    
    def test_process_request_no_phi(self):
        """Test processing request without PHI"""
        self.guardrail.register_user("guest1", AccessLevel.GUEST)
        
        text = "This is normal text"
        result = self.guardrail.process_request("guest1", text, "read")
        
        self.assertTrue(result['success'])
        self.assertFalse(result['phi_detected'])
        self.assertEqual(result['phi_count'], 0)
    
    def test_audit_trail_generation(self):
        """Test audit trail is generated"""
        self.guardrail.register_user("user1", AccessLevel.CLINICIAN)
        
        self.guardrail.process_request("user1", "SSN: 123-45-6789", "read")
        self.guardrail.process_request("user1", "Normal text", "write")
        
        audit_trail = self.guardrail.get_audit_trail("user1")
        self.assertEqual(len(audit_trail), 2)
    
    def test_compliance_level_update(self):
        """Test updating compliance level"""
        self.guardrail.set_compliance_level(ComplianceLevel.STRICT)
        self.assertEqual(self.guardrail.compliance_level, ComplianceLevel.STRICT)
        self.assertEqual(self.guardrail.enforcer.compliance_level, ComplianceLevel.STRICT)
    
    def test_strict_mode_blocks_unauthorized(self):
        """Test strict mode blocks unauthorized PHI access"""
        self.guardrail.set_compliance_level(ComplianceLevel.STRICT)
        self.guardrail.register_user("researcher1", AccessLevel.RESEARCHER)
        
        text = "SSN: 123-45-6789"
        result = self.guardrail.process_request("researcher1", text, "read")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['action_taken'], 'PHI access denied')
    
    def test_multiple_phi_entities(self):
        """Test handling multiple PHI entities"""
        self.guardrail.register_user("doc1", AccessLevel.CLINICIAN)
        
        text = "SSN: 123-45-6789, Phone: 555-123-4567, Email: test@example.com"
        result = self.guardrail.process_request("doc1", text, "read")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['phi_count'], 3)
        self.assertEqual(len(result['phi_entities']), 3)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_text(self):
        """Test handling empty text"""
        detector = PHIDetector()
        entities = detector.detect("")
        self.assertEqual(len(entities), 0)
    
    def test_very_long_text(self):
        """Test handling very long text"""
        detector = PHIDetector()
        text = "Normal text " * 1000 + " SSN: 123-45-6789"
        entities = detector.detect(text)
        self.assertEqual(len(entities), 1)
    
    def test_overlapping_patterns(self):
        """Test handling potentially overlapping patterns"""
        detector = PHIDetector()
        text = "MRN: 1234567 and Patient ID: ABC123456"
        entities = detector.detect(text)
        self.assertGreater(len(entities), 0)
    
    def test_case_insensitive_detection(self):
        """Test case-insensitive pattern detection"""
        detector = PHIDetector()
        text1 = "MRN: 1234567"
        text2 = "mrn: 1234567"
        entities1 = detector.detect(text1)
        entities2 = detector.detect(text2)
        self.assertEqual(len(entities1), len(entities2))
    
    def test_unregistered_user_request(self):
        """Test request from unregistered user"""
        guardrail = AIGuardrail(ComplianceLevel.MODERATE)
        text = "SSN: 123-45-6789"
        result = guardrail.process_request("unknown_user", text, "read")
        self.assertFalse(result['success'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
