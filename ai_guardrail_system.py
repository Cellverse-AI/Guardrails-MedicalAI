"""
AI Guardrail System for PHI Detection, Redaction, and Compliance Enforcement
Handles Protected Health Information (PHI) detection, automatic redaction, 
access monitoring, and HIPAA compliance enforcement.
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance enforcement levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


class AccessLevel(Enum):
    """User access levels"""
    ADMIN = "admin"
    CLINICIAN = "clinician"
    RESEARCHER = "researcher"
    PATIENT = "patient"
    GUEST = "guest"


@dataclass
class PHIEntity:
    """Represents a detected PHI entity"""
    entity_type: str
    value: str
    start_pos: int
    end_pos: int
    confidence: float
    redacted_value: str


@dataclass
class AccessLog:
    """Represents an access event"""
    user_id: str
    access_level: str
    timestamp: str
    action: str
    resource: str
    phi_detected: bool
    phi_count: int
    status: str
    details: str


class PHIDetector:
    """Detects Protected Health Information patterns"""
    
    PATTERNS = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'medical_record': r'\b(MRN|MR#|Medical Record)\s*[:#]?\s*(\d{6,10})\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'date_of_birth': r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12][0-9]|3[01])[-/](19|20)\d{2}\b',
        'patient_id': r'\b(PID|Patient ID|PatientID)\s*[:#]?\s*([A-Z0-9]{6,12})\b',
        'insurance_id': r'\b(Insurance ID|Policy)\s*[:#]?\s*([A-Z0-9]{8,15})\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        'hospital_id': r'\b(Hospital ID|Facility ID)\s*[:#]?\s*([A-Z0-9]{4,8})\b',
        'prescription': r'\b(Rx|Prescription)\s*[:#]?\s*([A-Z0-9]{6,10})\b',
    }
    
    def __init__(self):
        self.compiled_patterns = {
            key: re.compile(pattern, re.IGNORECASE)
            for key, pattern in self.PATTERNS.items()
        }
    
    def detect(self, text: str) -> List[PHIEntity]:
        """Detect PHI entities in text"""
        entities = []
        
        for entity_type, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                entity = PHIEntity(
                    entity_type=entity_type,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,
                    redacted_value=self._generate_redaction(entity_type)
                )
                entities.append(entity)
        
        return sorted(entities, key=lambda x: x.start_pos)
    
    @staticmethod
    def _generate_redaction(entity_type: str) -> str:
        """Generate appropriate redaction for entity type"""
        redactions = {
            'ssn': '[SSN]',
            'medical_record': '[MRN]',
            'phone': '[PHONE]',
            'email': '[EMAIL]',
            'date_of_birth': '[DOB]',
            'patient_id': '[PATIENT_ID]',
            'insurance_id': '[INSURANCE_ID]',
            'credit_card': '[CREDIT_CARD]',
            'ip_address': '[IP_ADDRESS]',
            'hospital_id': '[HOSPITAL_ID]',
            'prescription': '[RX]',
        }
        return redactions.get(entity_type, '[REDACTED]')


class PHIRedactor:
    """Redacts PHI from text"""
    
    @staticmethod
    def redact(text: str, entities: List[PHIEntity]) -> Tuple[str, int]:
        """Redact PHI entities from text"""
        if not entities:
            return text, 0
        
        sorted_entities = sorted(entities, key=lambda x: x.start_pos, reverse=True)
        
        redacted_text = text
        for entity in sorted_entities:
            redacted_text = (
                redacted_text[:entity.start_pos] +
                entity.redacted_value +
                redacted_text[entity.end_pos:]
            )
        
        return redacted_text, len(entities)
    
    @staticmethod
    def partial_redact(text: str, entities: List[PHIEntity], 
                      show_chars: int = 2) -> str:
        """Partially redact PHI (show first/last N characters)"""
        sorted_entities = sorted(entities, key=lambda x: x.start_pos, reverse=True)
        
        redacted_text = text
        for entity in sorted_entities:
            value = entity.value
            if len(value) > show_chars * 2:
                partial = value[:show_chars] + '*' * (len(value) - show_chars * 2) + value[-show_chars:]
            else:
                partial = '*' * len(value)
            
            redacted_text = (
                redacted_text[:entity.start_pos] +
                partial +
                redacted_text[entity.end_pos:]
            )
        
        return redacted_text


class AccessControl:
    """Manages access control and permissions"""
    
    PERMISSIONS = {
        AccessLevel.ADMIN: {
            'view_phi': True,
            'redact_phi': True,
            'view_logs': True,
            'modify_policies': True,
            'export_data': True
        },
        AccessLevel.CLINICIAN: {
            'view_phi': True,
            'redact_phi': False,
            'view_logs': False,
            'modify_policies': False,
            'export_data': False
        },
        AccessLevel.RESEARCHER: {
            'view_phi': False,
            'redact_phi': False,
            'view_logs': False,
            'modify_policies': False,
            'export_data': True
        },
        AccessLevel.PATIENT: {
            'view_phi': True,
            'redact_phi': False,
            'view_logs': False,
            'modify_policies': False,
            'export_data': False
        },
        AccessLevel.GUEST: {
            'view_phi': False,
            'redact_phi': False,
            'view_logs': False,
            'modify_policies': False,
            'export_data': False
        }
    }
    
    def __init__(self):
        self.user_roles: Dict[str, AccessLevel] = {}
    
    def register_user(self, user_id: str, access_level: AccessLevel):
        """Register user with access level"""
        self.user_roles[user_id] = access_level
        logger.info(f"User {user_id} registered with access level {access_level.value}")
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has permission"""
        if user_id not in self.user_roles:
            return False
        
        access_level = self.user_roles[user_id]
        return self.PERMISSIONS[access_level].get(permission, False)
    
    def get_access_level(self, user_id: str) -> Optional[AccessLevel]:
        """Get user's access level"""
        return self.user_roles.get(user_id)


class ComplianceEnforcer:
    """Enforces compliance policies"""
    
    def __init__(self, compliance_level: ComplianceLevel = ComplianceLevel.MODERATE):
        self.compliance_level = compliance_level
        self.access_logs: List[AccessLog] = []
    
    def enforce(self, user_id: str, text: str, access_control: AccessControl,
                phi_entities: List[PHIEntity]) -> Tuple[str, bool, str]:
        """Enforce compliance policy"""
        access_level = access_control.get_access_level(user_id)
        
        if not access_level:
            return text, False, "User not registered"
        
        has_phi = len(phi_entities) > 0
        
        if self.compliance_level == ComplianceLevel.STRICT:
            if has_phi and not access_control.has_permission(user_id, 'view_phi'):
                return text, False, "PHI access denied"
            return text, True, "allowed"
        
        elif self.compliance_level == ComplianceLevel.MODERATE:
            if has_phi:
                if access_control.has_permission(user_id, 'view_phi'):
                    return text, True, "allowed_with_phi"
                else:
                    redacted_text, count = PHIRedactor.redact(text, phi_entities)
                    return redacted_text, True, "redacted"
            return text, True, "allowed"
        
        else:
            return text, True, "allowed"
    
    def log_access(self, user_id: str, access_level: str, action: str,
                   resource: str, phi_detected: bool, phi_count: int,
                   status: str, details: str = ""):
        """Log access event"""
        log_entry = AccessLog(
            user_id=user_id,
            access_level=access_level,
            timestamp=datetime.now().isoformat(),
            action=action,
            resource=resource,
            phi_detected=phi_detected,
            phi_count=phi_count,
            status=status,
            details=details
        )
        self.access_logs.append(log_entry)
        logger.info(f"Access logged: {user_id} - {action} - {status}")
    
    def get_audit_trail(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get audit trail"""
        logs = self.access_logs
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        return [asdict(log) for log in logs]


class AIGuardrail:
    """Main AI Guardrail system"""
    
    def __init__(self, compliance_level: ComplianceLevel = ComplianceLevel.MODERATE):
        self.detector = PHIDetector()
        self.redactor = PHIRedactor()
        self.access_control = AccessControl()
        self.enforcer = ComplianceEnforcer(compliance_level)
        self.compliance_level = compliance_level
    
    def process_request(self, user_id: str, text: str, action: str = "read") -> Dict:
        """Process a request with full guardrail enforcement"""
        phi_entities = self.detector.detect(text)
        
        processed_text, allowed, action_taken = self.enforcer.enforce(
            user_id, text, self.access_control, phi_entities
        )
        
        access_level = self.access_control.get_access_level(user_id)
        self.enforcer.log_access(
            user_id=user_id,
            access_level=access_level.value if access_level else "unknown",
            action=action,
            resource="text_input",
            phi_detected=len(phi_entities) > 0,
            phi_count=len(phi_entities),
            status="allowed" if allowed else "blocked",
            details=action_taken
        )
        
        return {
            'success': allowed,
            'processed_text': processed_text,
            'phi_detected': len(phi_entities) > 0,
            'phi_count': len(phi_entities),
            'phi_entities': [
                {
                    'type': e.entity_type,
                    'value': e.value if allowed else '[REDACTED]',
                    'position': (e.start_pos, e.end_pos),
                    'confidence': e.confidence
                }
                for e in phi_entities
            ],
            'action_taken': action_taken,
            'message': 'Request processed successfully' if allowed else 'Request blocked due to compliance policy'
        }
    
    def register_user(self, user_id: str, access_level: AccessLevel):
        """Register a user"""
        self.access_control.register_user(user_id, access_level)
    
    def get_audit_trail(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get audit trail"""
        return self.enforcer.get_audit_trail(user_id)
    
    def set_compliance_level(self, level: ComplianceLevel):
        """Update compliance level"""
        self.compliance_level = level
        self.enforcer.compliance_level = level
        logger.info(f"Compliance level updated to {level.value}")
