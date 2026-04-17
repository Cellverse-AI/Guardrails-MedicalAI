"""
Example usage of the Histopathology H&E Image Validation Guardrail
Demonstrates validation of histopathology images for dimensions, magnification, and H&E staining
"""

from histopathology_image_guardrail import (
    HistopathologyImageGuardrail,
    ValidationStatus
)
from PIL import Image
import numpy as np


def create_sample_he_image(width: int, height: int, filename: str):
    """
    Create a sample H&E-like image for testing
    
    Args:
        width: Image width
        height: Image height
        filename: Output filename
    """
    # Create image with H&E-like colors
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add hematoxylin (blue/purple) regions - nuclei
    image[::4, ::4] = [150, 150, 220]  # Blue/purple for nuclei
    
    # Add eosin (pink/red) regions - cytoplasm
    image[1::4, 1::4] = [230, 180, 200]  # Pink for cytoplasm
    image[2::4, 2::4] = [240, 190, 210]  # Pink variations
    
    # Add some tissue background
    image[3::4, 3::4] = [245, 200, 215]  # Light pink background
    
    # Save image
    img = Image.fromarray(image, 'RGB')
    img.save(filename)
    print(f"Created sample H&E image: {filename} ({width}x{height})")


def example_valid_image():
    """Example 1: Valid H&E image with correct dimensions and magnification"""
    print("\n" + "="*70)
    print("EXAMPLE 1: VALID H&E IMAGE")
    print("="*70)
    
    # Create a valid sample image (512x512, multiple of 256)
    create_sample_he_image(512, 512, "sample_he_valid.png")
    
    # Initialize guardrail with k=256
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    
    # Validate image with 20x magnification
    result = guardrail.validate_image(
        image_path="sample_he_valid.png",
        magnification=20
    )
    
    # Print summary
    print(guardrail.get_validation_summary(result))


def example_invalid_dimensions():
    """Example 2: Invalid dimensions (not multiple of k)"""
    print("\n" + "="*70)
    print("EXAMPLE 2: INVALID DIMENSIONS")
    print("="*70)
    
    # Create image with invalid dimensions (500x500, not multiple of 256)
    create_sample_he_image(500, 500, "sample_he_invalid_dim.png")
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    
    result = guardrail.validate_image(
        image_path="sample_he_invalid_dim.png",
        magnification=20
    )
    
    print(guardrail.get_validation_summary(result))


def example_invalid_magnification():
    """Example 3: Invalid magnification"""
    print("\n" + "="*70)
    print("EXAMPLE 3: INVALID MAGNIFICATION")
    print("="*70)
    
    # Create valid image
    create_sample_he_image(512, 512, "sample_he_invalid_mag.png")
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    
    # Try with invalid magnification (10x instead of 20x or 40x)
    result = guardrail.validate_image(
        image_path="sample_he_invalid_mag.png",
        magnification=10
    )
    
    print(guardrail.get_validation_summary(result))


def example_non_he_staining():
    """Example 4: Non-H&E stained image"""
    print("\n" + "="*70)
    print("EXAMPLE 4: NON-H&E STAINED IMAGE")
    print("="*70)
    
    # Create a grayscale-like image (not H&E)
    image = np.ones((512, 512, 3), dtype=np.uint8) * 128  # Gray image
    img = Image.fromarray(image, 'RGB')
    img.save("sample_non_he.png")
    print("Created non-H&E image: sample_non_he.png")
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    
    result = guardrail.validate_image(
        image_path="sample_non_he.png",
        magnification=20
    )
    
    print(guardrail.get_validation_summary(result))


def example_custom_tile_size():
    """Example 5: Custom tile size (k)"""
    print("\n" + "="*70)
    print("EXAMPLE 5: CUSTOM TILE SIZE")
    print("="*70)
    
    # Create image that's multiple of 128 but not 256
    create_sample_he_image(384, 384, "sample_he_custom_k.png")
    
    # Test with k=256 (should fail)
    print("\n--- Testing with k=256 ---")
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    result = guardrail.validate_image(
        image_path="sample_he_custom_k.png",
        magnification=20
    )
    print(f"Dimension Check: {'PASSED' if result.dimension_check else 'FAILED'}")
    print(f"Details: {result.details['dimension_validation']}")
    
    # Test with k=128 (should pass)
    print("\n--- Testing with k=128 ---")
    guardrail.set_tile_size(128)
    result = guardrail.validate_image(
        image_path="sample_he_custom_k.png",
        magnification=20
    )
    print(f"Dimension Check: {'PASSED' if result.dimension_check else 'PASSED'}")
    print(f"Details: {result.details['dimension_validation']}")


def example_40x_magnification():
    """Example 6: Valid 40x magnification"""
    print("\n" + "="*70)
    print("EXAMPLE 6: 40X MAGNIFICATION")
    print("="*70)
    
    create_sample_he_image(1024, 1024, "sample_he_40x.png")
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    
    result = guardrail.validate_image(
        image_path="sample_he_40x.png",
        magnification=40
    )
    
    print(guardrail.get_validation_summary(result))


def example_batch_validation():
    """Example 7: Batch validation of multiple images"""
    print("\n" + "="*70)
    print("EXAMPLE 7: BATCH VALIDATION")
    print("="*70)
    
    # Create multiple test images
    test_images = [
        ("sample_batch_1.png", 512, 512, 20, True),
        ("sample_batch_2.png", 768, 768, 40, True),
        ("sample_batch_3.png", 500, 500, 20, False),  # Invalid dimensions
        ("sample_batch_4.png", 1024, 1024, 60, False),  # Invalid magnification
    ]
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    
    results = []
    for filename, width, height, mag, _ in test_images:
        create_sample_he_image(width, height, filename)
        result = guardrail.validate_image(filename, mag)
        results.append((filename, result))
    
    # Summary table
    print("\n--- Batch Validation Summary ---")
    print(f"{'Image':<25} {'Dimensions':<15} {'Mag':<8} {'Status':<10}")
    print("-" * 70)
    
    for filename, result in results:
        dims = f"{result.details['image_dimensions'][0]}x{result.details['image_dimensions'][1]}"
        mag = f"{result.details['magnification']}x"
        status = "PASSED" if result.passed else "FAILED"
        print(f"{filename:<25} {dims:<15} {mag:<8} {status:<10}")
    
    # Detailed results for failed validations
    print("\n--- Failed Validation Details ---")
    for filename, result in results:
        if not result.passed:
            print(f"\n{filename}:")
            print(f"  Message: {result.message}")
            if not result.dimension_check:
                print(f"  Dimension Issue: {result.details['dimension_validation']}")
            if not result.magnification_check:
                print(f"  Magnification Issue: {result.details['magnification_validation']}")


def example_programmatic_access():
    """Example 8: Programmatic access to validation results"""
    print("\n" + "="*70)
    print("EXAMPLE 8: PROGRAMMATIC ACCESS")
    print("="*70)
    
    create_sample_he_image(512, 512, "sample_programmatic.png")
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    result = guardrail.validate_image("sample_programmatic.png", 20)
    
    # Access individual validation results
    print(f"\nValidation Status: {result.status.value}")
    print(f"Overall Passed: {result.passed}")
    print(f"\nIndividual Checks:")
    print(f"  - Dimensions: {result.dimension_check}")
    print(f"  - Magnification: {result.magnification_check}")
    print(f"  - H&E Staining: {result.staining_check}")
    
    # Access detailed information
    print(f"\nDetailed Information:")
    print(f"  - Image Size: {result.details['image_dimensions']}")
    print(f"  - Tile Size (k): {result.details['tile_size_k']}")
    print(f"  - Hematoxylin %: {result.details['staining_validation']['hematoxylin_percentage']}")
    print(f"  - Eosin %: {result.details['staining_validation']['eosin_percentage']}")
    
    # Use in conditional logic
    if result.passed:
        print("\n✓ Image is ready for processing!")
    else:
        print(f"\n✗ Image validation failed: {result.message}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("HISTOPATHOLOGY H&E IMAGE VALIDATION GUARDRAIL - EXAMPLES")
    print("="*70)
    
    example_valid_image()
    example_invalid_dimensions()
    example_invalid_magnification()
    example_non_he_staining()
    example_custom_tile_size()
    example_40x_magnification()
    example_batch_validation()
    example_programmatic_access()
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
