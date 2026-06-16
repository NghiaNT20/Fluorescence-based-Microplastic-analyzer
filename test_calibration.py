"""
Quick Test Script for Camera Calibration Feature

This script demonstrates how to use the camera calibration functionality
in the Microplastic Analyzer.
"""

from src.core.calibration import CameraCalibration
import math

def example_1_reference_calibration():
    """Example 1: Calibrate using a reference object"""
    print("=" * 60)
    print("EXAMPLE 1: Reference Object Calibration")
    print("=" * 60)
    
    # Create calibration object
    calib = CameraCalibration()
    
    # Scenario: You have a 100 μm bead that measures 40 pixels in your image
    reference_size_um = 100.0  # Known size in micrometers
    measured_pixels = 40.0      # Measured in image
    
    # Calibrate
    calib.calibrate_from_reference(reference_size_um, measured_pixels)
    
    # Test with a particle
    particle_area_pixels = 500
    area_um2 = calib.pixel_area_to_um2(particle_area_pixels)
    diameter_um = calib.calculate_real_diameter(particle_area_pixels)
    
    print(f"\nExample particle (500 pixels² area):")
    print(f"  Real area: {area_um2:.1f} μm²")
    print(f"  Diameter: {diameter_um:.1f} μm")
    print(f"  Category: {calib.get_size_category(diameter_um)}")
    
    # Save calibration
    calib.save_calibration('calibration_reference.json')
    print(f"\n✓ Saved to calibration_reference.json")
    print()


def example_2_camera_parameters():
    """Example 2: Calibrate using camera parameters"""
    print("=" * 60)
    print("EXAMPLE 2: Camera Parameters Calibration")
    print("=" * 60)
    
    # Your camera setup
    sensor_diagonal_mm = 5.76  # 1/2.5" sensor
    fov_degrees = 94.5         # Field of view
    resolution_width = 3840    # Image width in pixels
    
    # Test different focal lengths and working distances
    scenarios = [
        {'focal': 2.1, 'distance': 5.0, 'name': 'Wide angle, 5mm depth'},
        {'focal': 2.8, 'distance': 5.0, 'name': 'Standard, 5mm depth'},
        {'focal': 3.6, 'distance': 5.0, 'name': 'Narrow angle, 5mm depth'},
        {'focal': 2.8, 'distance': 10.0, 'name': 'Standard, 10mm depth'},
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        
        # Calculate sensor width (16:9 aspect ratio)
        aspect_ratio = 16/9
        sensor_width_mm = sensor_diagonal_mm * math.sqrt(aspect_ratio**2 / (aspect_ratio**2 + 1))
        
        # Calculate FOV at working distance
        fov_width_mm = (sensor_width_mm * scenario['distance']) / scenario['focal']
        
        # Calculate calibration
        um_per_pixel = (fov_width_mm * 1000) / resolution_width
        
        print(f"  Focal length: {scenario['focal']} mm")
        print(f"  Working distance: {scenario['distance']} mm")
        print(f"  FOV: {fov_width_mm:.2f} mm width")
        print(f"  Calibration: {um_per_pixel:.3f} μm/pixel")
        print(f"  Min detectable: {3 * um_per_pixel:.1f} μm")
        print(f"  10 μm particle: {10/um_per_pixel:.1f} pixels")
        print(f"  100 μm particle: {100/um_per_pixel:.1f} pixels")
    
    print()


def example_3_gui_integration():
    """Example 3: How calibration works in GUI"""
    print("=" * 60)
    print("EXAMPLE 3: GUI Integration")
    print("=" * 60)
    
    print("""
In the GUI, you can:

1. Click "📐 Camera Calibration" button
2. Choose calibration method:
   
   Tab 1: Camera Parameters
   - Enter sensor size (e.g., 1/2.5")
   - Enter resolution (e.g., 3840×2160)
   - Enter FOV (e.g., 94.5°)
   - Enter focal length (e.g., 2.8 mm)
   - Enter working distance (e.g., 5 mm)
   - Click "Calculate Calibration"
   
   Tab 2: Reference Object
   - Enter known size (e.g., 100 μm)
   - Enter measured pixels (e.g., 40 pixels)
   - Click "Calculate from Reference"
   
3. Click "Save Calibration" to save for later
4. Click "Apply & Close"

After calibration:
- Results table shows: Area (μm²), Diameter (μm), Area (px)
- Size categories are automatically assigned
- All measurements use real-world units

    """)


def example_4_full_workflow():
    """Example 4: Complete workflow with calibration"""
    print("=" * 60)
    print("EXAMPLE 4: Complete Workflow")
    print("=" * 60)
    
    # Step 1: Create calibration
    calib = CameraCalibration()
    
    # Option A: From parameters
    print("\nStep 1: Calibrate camera")
    print("  Using: 2.8mm focal length, 5mm working distance")
    
    sensor_width_mm = 5.03
    focal_length_mm = 2.8
    working_distance_mm = 5.0
    resolution_width = 3840
    aspect_ratio = 16/9
    
    fov_width_mm = (sensor_width_mm * working_distance_mm) / focal_length_mm
    resolution_height = int(resolution_width / aspect_ratio)
    fov_height_mm = fov_width_mm / aspect_ratio
    
    calib.calibrate_from_fov(fov_width_mm, fov_height_mm, resolution_width, resolution_height)
    
    # Step 2: Analyze particles (simulated)
    print("\nStep 2: Analyze particles")
    particles = [
        {'id': 1, 'area_px': 25, 'shape': 'Small'},
        {'id': 2, 'area_px': 156, 'shape': 'Medium'},
        {'id': 3, 'area_px': 625, 'shape': 'Large'},
        {'id': 4, 'area_px': 2500, 'shape': 'Very Large'},
    ]
    
    print("\n{:<5} {:<12} {:<12} {:<15} {:<20}".format(
        "ID", "Area (px)", "Area (μm²)", "Diameter (μm)", "Category"
    ))
    print("-" * 70)
    
    for p in particles:
        area_um2 = calib.pixel_area_to_um2(p['area_px'])
        diameter_um = calib.calculate_real_diameter(p['area_px'])
        category = calib.get_size_category(diameter_um)
        
        print("{:<5} {:<12.0f} {:<12.1f} {:<15.1f} {:<20}".format(
            p['id'], p['area_px'], area_um2, diameter_um, category
        ))
    
    # Step 3: Save results
    print("\nStep 3: Save calibration")
    calib.save_calibration('calibration_workflow.json')
    print("  ✓ Saved to calibration_workflow.json")
    
    # Step 4: Load in future sessions
    print("\nStep 4: Load calibration (in future session)")
    calib2 = CameraCalibration()
    calib2.load_calibration('calibration_workflow.json')
    print(f"  ✓ Loaded: {calib2.um_per_pixel_x:.3f} μm/pixel")
    print()


def example_5_validation():
    """Example 5: Validate calibration accuracy"""
    print("=" * 60)
    print("EXAMPLE 5: Calibration Validation")
    print("=" * 60)
    
    # Calibrate
    calib = CameraCalibration()
    calib.calibrate_from_reference(100, 40)  # 100 μm = 40 pixels
    
    # Test with known-size objects
    test_objects = [
        {'name': '25 μm bead', 'expected_um': 25, 'measured_px': 10},
        {'name': '50 μm bead', 'expected_um': 50, 'measured_px': 20},
        {'name': '100 μm bead', 'expected_um': 100, 'measured_px': 40},
        {'name': '200 μm bead', 'expected_um': 200, 'measured_px': 80},
    ]
    
    print(f"\nCalibration: {calib.um_per_pixel_x:.3f} μm/pixel\n")
    print("{:<15} {:<12} {:<12} {:<10}".format(
        "Object", "Expected", "Measured", "Error %"
    ))
    print("-" * 50)
    
    errors = []
    for obj in test_objects:
        predicted = calib.pixel_length_to_um(obj['measured_px'])
        error = abs(predicted - obj['expected_um']) / obj['expected_um'] * 100
        errors.append(error)
        
        print("{:<15} {:<12.1f} {:<12.1f} {:<10.2f}".format(
            obj['name'], obj['expected_um'], predicted, error
        ))
    
    avg_error = sum(errors) / len(errors)
    print(f"\nAverage error: {avg_error:.2f}%")
    
    if avg_error < 5:
        print("✓ Calibration is EXCELLENT (error <5%)")
    elif avg_error < 10:
        print("✓ Calibration is GOOD (error <10%)")
    else:
        print("⚠ Calibration needs improvement (error >10%)")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  CAMERA CALIBRATION EXAMPLES")
    print("  Microplastic Analyzer")
    print("=" * 60 + "\n")
    
    # Run examples
    example_1_reference_calibration()
    example_2_camera_parameters()
    example_3_gui_integration()
    example_4_full_workflow()
    example_5_validation()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print()
    print("To use in GUI:")
    print("  1. Run: python main.py")
    print("  2. Click '📐 Camera Calibration' button")
    print("  3. Input your parameters")
    print("  4. Analyze images with real-world sizes!")
    print()
