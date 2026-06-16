# Tutorial: Camera Calibration for Microplastic Size Measurement

## Introduction

This tutorial walks you through calibrating your camera system to measure microplastic particle sizes accurately. By the end, you'll be able to convert pixel measurements to real-world micrometers.

**Time required:** 15-30 minutes  
**Difficulty:** Beginner-Intermediate  

---

## Materials Needed

1. **Calibration reference** (choose one):
   - Calibrated microbeads (50, 100, or 200 μm)
   - Stage micrometer or graticule
   - Known-size microplastic standards
   
2. **Your imaging setup:**
   - Camera (3840×2160 resolution)
   - 5mm water layer
   - Proper lighting

3. **Software:**
   - Python with OpenCV, NumPy
   - Your microplastic analyzer

---

## Tutorial 1: Basic Calibration with Reference Object

### Step 1: Prepare Reference Image

1. Place your calibration reference (e.g., 100 μm bead) in the water layer
2. Ensure it's in the same focal plane as your samples
3. Take a clear, well-focused image
4. Save as `reference.jpg`

### Step 2: Measure Reference in Pixels

```python
import cv2
import numpy as np

# Load reference image
img = cv2.imread('reference.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Threshold to isolate reference
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

# Find contour
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Get the largest contour (your reference)
if contours:
    largest = max(contours, key=cv2.contourArea)
    
    # Calculate diameter
    area = cv2.contourArea(largest)
    diameter_pixels = 2 * np.sqrt(area / np.pi)
    
    print(f"Reference measured: {diameter_pixels:.1f} pixels")
    
    # Or use bounding box width
    x, y, w, h = cv2.boundingRect(largest)
    print(f"Bounding box width: {w} pixels")
    print(f"Bounding box height: {h} pixels")
```

**Example output:**
```
Reference measured: 40.3 pixels
Bounding box width: 42 pixels
Bounding box height: 39 pixels
```

### Step 3: Calculate Calibration Factor

```python
from src.core.calibration import CameraCalibration

# Known reference size
reference_size_um = 100  # micrometers

# Measured size from Step 2
measured_pixels = 40.3  # pixels

# Calibrate
calib = CameraCalibration()
calib.calibrate_from_reference(reference_size_um, measured_pixels)

# Save for future use
calib.save_calibration('calibration.json')
```

**Output:**
```
✓ Calibration complete: 2.481 μm/pixel (both axis)
✓ Calibration saved to calibration.json
```

### Step 4: Validate Calibration

Test with a different known-size object:

```python
# Load calibration
calib = CameraCalibration()
calib.load_calibration('calibration.json')

# Measure test object (e.g., 50 μm bead appears as 20 pixels)
test_pixels = 20
predicted_size = calib.pixel_length_to_um(test_pixels)

print(f"Test object: {predicted_size:.1f} μm")
# Expected: ~49.6 μm (close to 50 μm)
```

---

## Tutorial 2: Theoretical Calibration (No Reference)

If you don't have a calibration standard, use your camera specifications:

```python
from src.core.calibration import CameraCalibration

# Your camera setup
calib = CameraCalibration()
calib.calibrate_theoretical(
    sensor_width_mm=5.03,      # 1/2.5" sensor physical width
    fov_degrees=94.5,          # Your camera's field of view
    working_distance_mm=5.0,   # Water layer depth
    resolution_width_px=3840,  # Image width
    aspect_ratio=16/9          # 16:9 aspect ratio
)

# Save
calib.save_calibration('calibration_theoretical.json')
```

**Expected output:**
```
✓ Theoretical calibration:
  Focal length: 3.21 mm
  FOV: 7.85 × 4.41 mm
  X-axis: 2.044 μm/pixel
  Y-axis: 2.042 μm/pixel
✓ Calibration saved to calibration_theoretical.json
```

**Note:** Theoretical calibration is less accurate than reference-based (±10-15% vs ±3-5%). Use it as a starting point, then refine with a reference object.

---

## Tutorial 3: Integrate with Your Analysis

### Modify Your Analyzer

Add calibration to your existing analysis code:

```python
import cv2
from src.core.calibration import CameraCalibration
from src.analysis.deep_analyzer import analyze_deep

# Load calibration
calib = CameraCalibration()
calib.load_calibration('calibration.json')

# Load and analyze image
img = cv2.imread('microplastic_sample.jpg')
result = analyze_deep(img)

# Process each detected particle
for i, feature in enumerate(result.features):
    # Original pixel measurements
    area_px = feature['area']
    
    # Convert to real-world size
    area_um2 = calib.pixel_area_to_um2(area_px)
    diameter_um = calib.calculate_real_diameter(area_px)
    size_category = calib.get_size_category(diameter_um)
    
    # Display results
    print(f"Particle {i+1}:")
    print(f"  Area: {area_um2:.1f} μm²")
    print(f"  Diameter: {diameter_um:.1f} μm")
    print(f"  Category: {size_category}")
    print(f"  Shape: {feature['shape']}")
    print()
```

**Example output:**
```
Particle 1:
  Area: 1234.5 μm²
  Diameter: 39.6 μm
  Category: Small Microplastic (10-100 μm)
  Shape: Microbead/Pellet

Particle 2:
  Area: 3850.2 μm²
  Diameter: 70.0 μm
  Category: Small Microplastic (10-100 μm)
  Shape: Fragment
```

### Add to Feature Dictionary

```python
# Convert all features at once
for feature in result.features:
    enhanced_feature = calib.convert_features(feature)
    
    # Now has: area_um2, diameter_um, size_category, etc.
    print(f"{enhanced_feature['diameter_um']:.1f} μm - {enhanced_feature['size_category']}")
```

---

## Tutorial 4: Advanced - Multi-Point Calibration

For better accuracy, calibrate using multiple reference sizes:

```python
import numpy as np
from src.core.calibration import CameraCalibration

# Measure multiple references
references = [
    {'size_um': 25, 'measured_px': 10.2},
    {'size_um': 50, 'measured_px': 20.1},
    {'size_um': 100, 'measured_px': 40.3},
    {'size_um': 200, 'measured_px': 80.5},
]

# Calculate calibration factors
calibration_factors = []
for ref in references:
    factor = ref['size_um'] / ref['measured_px']
    calibration_factors.append(factor)
    print(f"{ref['size_um']:3d} μm / {ref['measured_px']:5.1f} px = {factor:.3f} μm/px")

# Average the calibration factors
avg_calibration = np.mean(calibration_factors)
std_calibration = np.std(calibration_factors)

print(f"\nAverage: {avg_calibration:.3f} ± {std_calibration:.3f} μm/pixel")

# Create calibration with average
calib = CameraCalibration(um_per_pixel=avg_calibration)
calib.save_calibration('calibration_multipoint.json')
```

**Example output:**
```
 25 μm /  10.2 px = 2.451 μm/px
 50 μm /  20.1 px = 2.488 μm/px
100 μm /  40.3 px = 2.481 μm/px
200 μm /  80.5 px = 2.484 μm/px

Average: 2.476 ± 0.015 μm/pixel
✓ Calibration saved to calibration_multipoint.json
```

Standard deviation <0.02 indicates good consistency!

---

## Tutorial 5: Create Calibration Report

Generate a validation report:

```python
from src.core.calibration import CameraCalibration
import json
from datetime import datetime

calib = CameraCalibration()
calib.load_calibration('calibration.json')

# Measure known test objects
test_objects = [
    {'name': '50μm bead', 'expected_um': 50, 'measured_px': 20.1},
    {'name': '100μm bead', 'expected_um': 100, 'measured_px': 40.3},
]

print("=== Calibration Validation Report ===")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"Calibration: {calib.um_per_pixel_x:.3f} μm/pixel\n")

print("Test Results:")
errors = []
for obj in test_objects:
    predicted = calib.pixel_length_to_um(obj['measured_px'])
    expected = obj['expected_um']
    error = abs(predicted - expected) / expected * 100
    errors.append(error)
    
    print(f"  {obj['name']}:")
    print(f"    Expected: {expected} μm")
    print(f"    Measured: {predicted:.1f} μm")
    print(f"    Error: {error:.1f}%")

avg_error = sum(errors) / len(errors)
print(f"\nAverage error: {avg_error:.1f}%")

if avg_error < 5:
    print("✓ Calibration is GOOD (error <5%)")
elif avg_error < 10:
    print("⚠ Calibration is ACCEPTABLE (error <10%)")
else:
    print("✗ Calibration needs improvement (error >10%)")
```

---

## Troubleshooting

### Issue 1: Calibration varies across image

**Cause:** Lens distortion (common with wide FOV lenses)

**Solution:**
```python
# Only calibrate using objects in the center 50% of image
# Or use OpenCV's camera calibration for distortion correction

import cv2
camera_matrix, dist_coeffs = cv2.calibrateCamera(...)
undistorted = cv2.undistort(img, camera_matrix, dist_coeffs)
```

### Issue 2: Measurements don't match expected values

**Checklist:**
- ✓ Working distance is exactly 5mm
- ✓ Reference is in same focal plane
- ✓ Water depth is consistent
- ✓ No air bubbles in water
- ✓ Reference size is accurate

### Issue 3: Small particles (<20 μm) unreliable

**Explanation:** At your resolution (~2.5 μm/pixel), a 20 μm particle is only 8 pixels. Accuracy degrades below 10-pixel diameter.

**Solutions:**
- Use higher magnification
- Higher resolution camera
- Accept ±10-15% error for small particles

---

## Best Practices Summary

1. **Calibrate regularly** - Monthly or after hardware changes
2. **Use multiple references** - Validate with 2-3 known sizes
3. **Document conditions** - Water depth, focus, lighting
4. **Save dated calibrations** - `calib_2026-04-08.json`
5. **Validate before use** - Quick test with known standard
6. **Exclude edge objects** - Higher distortion at image edges
7. **Average measurements** - Take 3-5 measurements per reference

---

## Next Steps

✓ **Complete calibration** using Tutorial 1 or 2  
✓ **Validate accuracy** with Tutorial 5  
✓ **Integrate with analyzer** using Tutorial 3  
✓ **Read full documentation** in `camera_calibration_guide.md`  

---

## Quick Commands

```bash
# Run calibration demo
python src/core/calibration.py

# Create calibration from your camera specs
python -c "from src.core.calibration import CameraCalibration; \
c = CameraCalibration(); \
c.calibrate_theoretical(5.03, 94.5, 5.0, 3840); \
c.save_calibration('calibration.json')"

# Test calibration
python -c "from src.core.calibration import CameraCalibration; \
c = CameraCalibration(); \
c.load_calibration('calibration.json'); \
print(f'Test: 100px = {c.pixel_length_to_um(100):.1f} μm')"
```

---

## Support & Resources

- **Full guide:** `docs/camera_calibration_guide.md`
- **Quick reference:** `docs/calibration_quick_reference.md`  
- **Code:** `src/core/calibration.py`
- **Calibration data:** `calibration.json`

---

**Good luck with your microplastic analysis!** 🔬
