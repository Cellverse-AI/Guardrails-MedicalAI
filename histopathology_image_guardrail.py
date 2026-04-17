"""
Histopathology H&E Image Validation Guardrail
Validates input histopathology H&E stained images for:
1. Image dimensions (must be multiple of k)
2. Magnification (20x or 40x)
3. H&E staining verification
"""

import numpy as np
from PIL import Image
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation status codes"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class ValidationResult:
    """Result of image validation"""
    status: ValidationStatus
    passed: bool
    dimension_check: bool
    magnification_check: bool
    staining_check: bool
    details: Dict
    message: str


class HistopathologyImageGuardrail:
    """
    Guardrail for validating histopathology H&E stained images
    """
    
    # H&E color characteristics in RGB space
    # Hematoxylin: blue/purple (nuclei)
    # Eosin: pink/red (cytoplasm, extracellular matrix)
    HEMATOXYLIN_RANGE = {
        'r': (100, 200),
        'g': (100, 200),
        'b': (180, 255)
    }
    
    EOSIN_RANGE = {
        'r': (200, 255),
        'g': (150, 220),
        'b': (180, 240)
    }
    
    VALID_MAGNIFICATIONS = [20, 40]
    
    def __init__(self, tile_size_k: int = 256):
        """
        Initialize the guardrail
        
        Args:
            tile_size_k: The tile size k that image dimensions must be a multiple of
        """
        self.tile_size_k = tile_size_k
        logger.info(f"Initialized HistopathologyImageGuardrail with tile_size_k={tile_size_k}")
    
    def validate_image(
        self,
        image_path: str,
        magnification: int,
        tile_size_k: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate a histopathology image
        
        Args:
            image_path: Path to the image file
            magnification: Declared magnification (20x or 40x)
            tile_size_k: Optional override for tile size k
            
        Returns:
            ValidationResult with detailed validation information
        """
        k = tile_size_k if tile_size_k is not None else self.tile_size_k
        
        try:
            # Load image
            image = Image.open(image_path)
            image_array = np.array(image)
            
            # Run validation checks
            dim_check, dim_details = self._validate_dimensions(image, k)
            mag_check, mag_details = self._validate_magnification(magnification)
            stain_check, stain_details = self._validate_he_staining(image_array)
            
            # Determine overall status
            all_passed = dim_check and mag_check and stain_check
            status = ValidationStatus.PASSED if all_passed else ValidationStatus.FAILED
            
            # Compile details
            details = {
                'image_path': image_path,
                'image_dimensions': (image.width, image.height),
                'tile_size_k': k,
                'magnification': magnification,
                'dimension_validation': dim_details,
                'magnification_validation': mag_details,
                'staining_validation': stain_details
            }
            
            # Generate message
            if all_passed:
                message = "All validation checks passed"
            else:
                failed_checks = []
                if not dim_check:
                    failed_checks.append("dimension")
                if not mag_check:
                    failed_checks.append("magnification")
                if not stain_check:
                    failed_checks.append("H&E staining")
                message = f"Validation failed: {', '.join(failed_checks)}"
            
            result = ValidationResult(
                status=status,
                passed=all_passed,
                dimension_check=dim_check,
                magnification_check=mag_check,
                staining_check=stain_check,
                details=details,
                message=message
            )
            
            logger.info(f"Validation completed: {message}")
            return result
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return ValidationResult(
                status=ValidationStatus.FAILED,
                passed=False,
                dimension_check=False,
                magnification_check=False,
                staining_check=False,
                details={'error': str(e)},
                message=f"Validation error: {str(e)}"
            )
    
    def _validate_dimensions(
        self,
        image: Image.Image,
        k: int
    ) -> Tuple[bool, Dict]:
        """
        Validate that image dimensions are multiples of k
        
        Args:
            image: PIL Image object
            k: Tile size that dimensions must be a multiple of
            
        Returns:
            Tuple of (passed, details_dict)
        """
        width, height = image.size
        
        width_valid = (width % k) == 0
        height_valid = (height % k) == 0
        
        details = {
            'width': width,
            'height': height,
            'tile_size_k': k,
            'width_multiple_of_k': width_valid,
            'height_multiple_of_k': height_valid,
            'width_remainder': width % k,
            'height_remainder': height % k
        }
        
        passed = width_valid and height_valid
        
        if not passed:
            if not width_valid:
                details['width_error'] = f"Width {width} is not a multiple of {k} (remainder: {width % k})"
            if not height_valid:
                details['height_error'] = f"Height {height} is not a multiple of {k} (remainder: {height % k})"
        
        return passed, details
    
    def _validate_magnification(
        self,
        magnification: int
    ) -> Tuple[bool, Dict]:
        """
        Validate that magnification is 20x or 40x
        
        Args:
            magnification: Declared magnification level
            
        Returns:
            Tuple of (passed, details_dict)
        """
        passed = magnification in self.VALID_MAGNIFICATIONS
        
        details = {
            'declared_magnification': magnification,
            'valid_magnifications': self.VALID_MAGNIFICATIONS,
            'is_valid': passed
        }
        
        if not passed:
            details['error'] = f"Magnification {magnification}x is not valid. Must be one of {self.VALID_MAGNIFICATIONS}"
        
        return passed, details
    
    def _validate_he_staining(
        self,
        image_array: np.ndarray
    ) -> Tuple[bool, Dict]:
        """
        Validate that image appears to be H&E stained
        
        Args:
            image_array: Numpy array of image (H, W, C)
            
        Returns:
            Tuple of (passed, details_dict)
        """
        # Convert to RGB if needed
        if len(image_array.shape) == 2:
            return False, {'error': 'Grayscale image detected, H&E images must be color'}
        
        if image_array.shape[2] < 3:
            return False, {'error': 'Image must have at least 3 color channels (RGB)'}
        
        # Extract RGB channels
        r_channel = image_array[:, :, 0]
        g_channel = image_array[:, :, 1]
        b_channel = image_array[:, :, 2]
        
        # Check for hematoxylin (blue/purple) presence
        hematoxylin_mask = (
            (r_channel >= self.HEMATOXYLIN_RANGE['r'][0]) &
            (r_channel <= self.HEMATOXYLIN_RANGE['r'][1]) &
            (g_channel >= self.HEMATOXYLIN_RANGE['g'][0]) &
            (g_channel <= self.HEMATOXYLIN_RANGE['g'][1]) &
            (b_channel >= self.HEMATOXYLIN_RANGE['b'][0]) &
            (b_channel <= self.HEMATOXYLIN_RANGE['b'][1])
        )
        
        # Check for eosin (pink/red) presence
        eosin_mask = (
            (r_channel >= self.EOSIN_RANGE['r'][0]) &
            (r_channel <= self.EOSIN_RANGE['r'][1]) &
            (g_channel >= self.EOSIN_RANGE['g'][0]) &
            (g_channel <= self.EOSIN_RANGE['g'][1]) &
            (b_channel >= self.EOSIN_RANGE['b'][0]) &
            (b_channel <= self.EOSIN_RANGE['b'][1])
        )
        
        # Calculate percentages
        total_pixels = image_array.shape[0] * image_array.shape[1]
        hematoxylin_percentage = (np.sum(hematoxylin_mask) / total_pixels) * 100
        eosin_percentage = (np.sum(eosin_mask) / total_pixels) * 100
        
        # Thresholds for H&E detection
        MIN_HEMATOXYLIN_PERCENTAGE = 5.0
        MIN_EOSIN_PERCENTAGE = 5.0
        
        hematoxylin_present = hematoxylin_percentage >= MIN_HEMATOXYLIN_PERCENTAGE
        eosin_present = eosin_percentage >= MIN_EOSIN_PERCENTAGE
        
        passed = hematoxylin_present and eosin_present
        
        details = {
            'hematoxylin_percentage': round(hematoxylin_percentage, 2),
            'eosin_percentage': round(eosin_percentage, 2),
            'hematoxylin_present': hematoxylin_present,
            'eosin_present': eosin_present,
            'min_hematoxylin_threshold': MIN_HEMATOXYLIN_PERCENTAGE,
            'min_eosin_threshold': MIN_EOSIN_PERCENTAGE,
            'color_distribution': {
                'mean_r': float(np.mean(r_channel)),
                'mean_g': float(np.mean(g_channel)),
                'mean_b': float(np.mean(b_channel))
            }
        }
        
        if not passed:
            errors = []
            if not hematoxylin_present:
                errors.append(f"Insufficient hematoxylin (blue/purple) detected: {hematoxylin_percentage:.2f}% < {MIN_HEMATOXYLIN_PERCENTAGE}%")
            if not eosin_present:
                errors.append(f"Insufficient eosin (pink/red) detected: {eosin_percentage:.2f}% < {MIN_EOSIN_PERCENTAGE}%")
            details['error'] = '; '.join(errors)
        
        return passed, details
    
    def set_tile_size(self, k: int):
        """Update the tile size k"""
        self.tile_size_k = k
        logger.info(f"Tile size updated to k={k}")
    
    def get_validation_summary(self, result: ValidationResult) -> str:
        """
        Generate a human-readable validation summary
        
        Args:
            result: ValidationResult object
            
        Returns:
            Formatted string summary
        """
        summary = []
        summary.append("="*70)
        summary.append("HISTOPATHOLOGY IMAGE VALIDATION REPORT")
        summary.append("="*70)
        summary.append(f"\nOverall Status: {result.status.value.upper()}")
        summary.append(f"Validation Passed: {result.passed}")
        summary.append(f"\n{result.message}")
        
        if 'image_path' in result.details:
            summary.append(f"\nImage: {result.details['image_path']}")
            summary.append(f"Dimensions: {result.details['image_dimensions']}")
            summary.append(f"Magnification: {result.details['magnification']}x")
            summary.append(f"Tile Size (k): {result.details['tile_size_k']}")
        
        summary.append("\n--- Validation Checks ---")
        summary.append(f"✓ Dimension Check: {'PASSED' if result.dimension_check else 'FAILED'}")
        summary.append(f"✓ Magnification Check: {'PASSED' if result.magnification_check else 'FAILED'}")
        summary.append(f"✓ H&E Staining Check: {'PASSED' if result.staining_check else 'FAILED'}")
        
        if 'dimension_validation' in result.details:
            dim = result.details['dimension_validation']
            summary.append(f"\n--- Dimension Details ---")
            summary.append(f"Width: {dim['width']} (multiple of {dim['tile_size_k']}: {dim['width_multiple_of_k']})")
            summary.append(f"Height: {dim['height']} (multiple of {dim['tile_size_k']}: {dim['height_multiple_of_k']})")
            if 'width_error' in dim:
                summary.append(f"Error: {dim['width_error']}")
            if 'height_error' in dim:
                summary.append(f"Error: {dim['height_error']}")
        
        if 'staining_validation' in result.details:
            stain = result.details['staining_validation']
            summary.append(f"\n--- H&E Staining Details ---")
            if 'hematoxylin_percentage' in stain:
                summary.append(f"Hematoxylin (blue/purple): {stain['hematoxylin_percentage']}%")
                summary.append(f"Eosin (pink/red): {stain['eosin_percentage']}%")
                summary.append(f"Color Distribution (RGB): ({stain['color_distribution']['mean_r']:.1f}, {stain['color_distribution']['mean_g']:.1f}, {stain['color_distribution']['mean_b']:.1f})")
            if 'error' in stain:
                summary.append(f"Error: {stain['error']}")
        
        summary.append("\n" + "="*70)
        
        return "\n".join(summary)
