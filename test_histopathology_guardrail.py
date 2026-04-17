"""
Quick test script for Histopathology H&E Image Validation Guardrail
"""

from histopathology_image_guardrail import HistopathologyImageGuardrail
from PIL import Image
import numpy as np


def create_test_he_image(filename: str, width: int, height: int):
    """Create a simple H&E-like test image"""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add hematoxylin (blue/purple) - nuclei
    image[::4, ::4] = [150, 150, 220]
    
    # Add eosin (pink/red) - cytoplasm
    image[1::4, 1::4] = [230, 180, 200]
    image[2::4, 2::4] = [240, 190, 210]
    image[3::4, 3::4] = [245, 200, 215]
    
    img = Image.fromarray(image, 'RGB')
    img.save(filename)
    return filename


def test_valid_image():
    """Test 1: Valid image (should pass all checks)"""
    print("\n" + "="*70)
    print("TEST 1: Valid H&E Image")
    print("="*70)
    
    # Create valid test image: 512x512 (multiple of 256), 20x magnification
    filename = create_test_he_image("test_valid.png", 512, 512)
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    result = guardrail.validate_image(filename, magnification=20)
    
    print(f"\n✓ Image created: {filename} (512x512)")
    print(f"✓ Magnification: 20x")
    print(f"✓ Tile size (k): 256")
    print(f"\nValidation Result: {'PASSED' if result.passed else 'FAILED'}")
    print(f"  - Dimension check: {'✓' if result.dimension_check else '✗'}")
    print(f"  - Magnification check: {'✓' if result.magnification_check else '✗'}")
    print(f"  - H&E staining check: {'✓' if result.staining_check else '✗'}")
    
    if result.passed:
        print("\n✓ SUCCESS: All validations passed!")
    else:
        print(f"\n✗ FAILED: {result.message}")


def test_invalid_dimensions():
    """Test 2: Invalid dimensions (should fail dimension check)"""
    print("\n" + "="*70)
    print("TEST 2: Invalid Dimensions")
    print("="*70)
    
    # Create image with invalid dimensions: 500x500 (not multiple of 256)
    filename = create_test_he_image("test_invalid_dim.png", 500, 500)
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    result = guardrail.validate_image(filename, magnification=20)
    
    print(f"\n✓ Image created: {filename} (500x500)")
    print(f"✓ Magnification: 20x")
    print(f"✓ Tile size (k): 256")
    print(f"\nValidation Result: {'PASSED' if result.passed else 'FAILED'}")
    print(f"  - Dimension check: {'✓' if result.dimension_check else '✗'}")
    print(f"  - Magnification check: {'✓' if result.magnification_check else '✗'}")
    print(f"  - H&E staining check: {'✓' if result.staining_check else '✗'}")
    
    if not result.dimension_check:
        dim = result.details['dimension_validation']
        print(f"\n✗ Dimension Error:")
        print(f"  Width: {dim['width']} (remainder: {dim['width_remainder']})")
        print(f"  Height: {dim['height']} (remainder: {dim['height_remainder']})")
        print(f"  Expected: multiples of {dim['tile_size_k']}")


def test_invalid_magnification():
    """Test 3: Invalid magnification (should fail magnification check)"""
    print("\n" + "="*70)
    print("TEST 3: Invalid Magnification")
    print("="*70)
    
    # Create valid image but with invalid magnification
    filename = create_test_he_image("test_invalid_mag.png", 512, 512)
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    result = guardrail.validate_image(filename, magnification=10)  # Invalid: 10x
    
    print(f"\n✓ Image created: {filename} (512x512)")
    print(f"✗ Magnification: 10x (INVALID)")
    print(f"✓ Tile size (k): 256")
    print(f"\nValidation Result: {'PASSED' if result.passed else 'FAILED'}")
    print(f"  - Dimension check: {'✓' if result.dimension_check else '✗'}")
    print(f"  - Magnification check: {'✓' if result.magnification_check else '✗'}")
    print(f"  - H&E staining check: {'✓' if result.staining_check else '✗'}")
    
    if not result.magnification_check:
        mag = result.details['magnification_validation']
        print(f"\n✗ Magnification Error:")
        print(f"  Provided: {mag['declared_magnification']}x")
        print(f"  Valid options: {mag['valid_magnifications']}")


def test_40x_magnification():
    """Test 4: Valid 40x magnification"""
    print("\n" + "="*70)
    print("TEST 4: Valid 40x Magnification")
    print("="*70)
    
    filename = create_test_he_image("test_40x.png", 1024, 1024)
    
    guardrail = HistopathologyImageGuardrail(tile_size_k=256)
    result = guardrail.validate_image(filename, magnification=40)
    
    print(f"\n✓ Image created: {filename} (1024x1024)")
    print(f"✓ Magnification: 40x")
    print(f"✓ Tile size (k): 256")
    print(f"\nValidation Result: {'PASSED' if result.passed else 'FAILED'}")
    print(f"  - Dimension check: {'✓' if result.dimension_check else '✗'}")
    print(f"  - Magnification check: {'✓' if result.magnification_check else '✗'}")
    print(f"  - H&E staining check: {'✓' if result.staining_check else '✗'}")
    
    if result.passed:
        print("\n✓ SUCCESS: 40x magnification validated!")


def test_custom_tile_size():
    """Test 5: Custom tile size"""
    print("\n" + "="*70)
    print("TEST 5: Custom Tile Size (k=128)")
    print("="*70)
    
    # Create image that's multiple of 128 but not 256
    filename = create_test_he_image("test_custom_k.png", 384, 384)
    
    # Test with k=128 (should pass)
    guardrail = HistopathologyImageGuardrail(tile_size_k=128)
    result = guardrail.validate_image(filename, magnification=20)
    
    print(f"\n✓ Image created: {filename} (384x384)")
    print(f"✓ Magnification: 20x")
    print(f"✓ Tile size (k): 128")
    print(f"\nValidation Result: {'PASSED' if result.passed else 'FAILED'}")
    print(f"  - Dimension check: {'✓' if result.dimension_check else '✗'}")
    
    if result.dimension_check:
        print("\n✓ SUCCESS: Custom tile size validated!")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("HISTOPATHOLOGY H&E IMAGE GUARDRAIL - QUICK TESTS")
    print("="*70)
    
    test_valid_image()
    test_invalid_dimensions()
    test_invalid_magnification()
    test_40x_magnification()
    test_custom_tile_size()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)
    print("\nTo run comprehensive examples, execute:")
    print("  python histopathology_guardrail_example.py")
    print("\nFor documentation, see:")
    print("  HISTOPATHOLOGY_GUARDRAIL_DOCUMENTATION.md")
    print()


if __name__ == "__main__":
    main()
