# Quick Reference: Size Calculation

## Your Camera Setup
```
Resolution: 3840 × 2160 pixels
Pixel Size: 1.45 μm × 1.45 μm  
FOV: 94.5° diagonal
Working Distance: 5 mm (water layer)
Target Size: 10-100 μm microplastics
```

---

## Quick Calibration (3 Steps)

### Step 1: Place Reference
- Use 100 μm calibration bead or ruler
- Place in same plane as your samples
- Take a clear image

### Step 2: Measure in Pixels
```python
from src.core.calibration import CameraCalibration

# Initialize calibration
calib = CameraCalibration()

# Measure reference (e.g., 100 μm bead appears as 40 pixels)
calib.calibrate_from_reference(reference_size_um=100, measured_pixels=40)
# Output: ✓ Calibration complete: 2.500 μm/pixel
```

### Step 3: Calculate Object Sizes
```python
# For particle with area = 500 pixels²
area_um2 = calib.pixel_area_to_um2(500)  # → 3125 μm²
diameter_um = calib.calculate_real_diameter(500)  # → 63.1 μm

# Save for later use
calib.save_calibration('calibration.json')
```

---

## Common Formulas

### Area Conversion
```python
area_μm² = area_pixels × (μm/pixel)²
```

### Diameter from Area
```python
diameter_μm = 2 × √(area_μm² / π)
```

### Pixels per Micrometer
```python
pixels/μm = measured_pixels / known_size_μm
```

### Minimum Detectable Size
```python
min_size_μm = 3 × μm_per_pixel  # 3-pixel minimum
```

---

## Integration Example

### Add to Your Analysis Code

```python
from src.core.calibration import CameraCalibration

# Load calibration
calib = CameraCalibration()
calib.load_calibration('calibration.json')

# In your analyzer loop
for contour in contours:
    area_pixels = cv2.contourArea(contour)
    
    # Get real-world size
    area_um2 = calib.pixel_area_to_um2(area_pixels)
    diameter_um = calib.calculate_real_diameter(area_pixels)
    size_category = calib.get_size_category(diameter_um)
    
    print(f"Particle: {diameter_um:.1f} μm ({size_category})")
```

### Batch Convert Features

```python
# If you have a feature dictionary
features = {
    'area': 500,
    'perimeter': 80,
    'bbox_width': 30,
    'bbox_height': 25
}

# Add calibrated measurements
features_with_real_sizes = calib.convert_features(features)

# Now includes: area_um2, diameter_um, perimeter_um, bbox_width_um, etc.
print(features_with_real_sizes['diameter_um'])  # → 63.1 μm
```

---

## Expected Values for Your Setup

| Metric | Value |
|--------|-------|
| **Theoretical μm/pixel** | 2-3 μm/pixel |
| **Minimum detectable size** | 6-10 μm |
| **Target size (10-100 μm)** | 3-40 pixels diameter |
| **FOV coverage** | ~8-10 mm width |
| **Accuracy** | ±3-5% |

---

## Size Categories

```python
<10 μm    → Nanoplastic
10-100 μm → Small Microplastic (YOUR TARGET)
100-1000  → Medium Microplastic  
1-5 mm    → Large Microplastic
>5 mm     → Macroplastic
```

---

## Validation Checklist

✓ **Calibration target** in same plane as samples  
✓ **Working distance** constant (5 mm)  
✓ **Focus** locked and consistent  
✓ **Multiple measurements** averaged  
✓ **Edge particles** excluded (distortion)  
✓ **Test objects** measured for validation  

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Sizes vary across image** | Check for lens distortion, recalibrate at center |
| **Results too large/small** | Verify working distance, check water depth |
| **Poor accuracy** | Use higher quality reference, average multiple measurements |
| **Small particles (~10 μm) unreliable** | Normal at resolution limit, increase magnification |

---

## Pro Tips

1. **Calibrate monthly** or after any hardware changes
2. **Use multiple reference sizes** (e.g., 50, 100, 200 μm)
3. **Save calibration files** with date: `calib_2026-04-08.json`
4. **Document your setup** (water depth, focus settings, etc.)
5. **Validate with standards** before each session

---

## File Locations

```
calibration.json              → Saved calibration data
src/core/calibration.py       → Calibration module
docs/camera_calibration_guide.md → Full documentation
```

---

## Command Line Usage

```bash
# Run calibration demo
python src/core/calibration.py

# Test with your settings
python -c "
from src.core.calibration import CameraCalibration
calib = CameraCalibration()
calib.calibrate_theoretical(5.03, 94.5, 5.0, 3840)
print(f'Your setup: {calib.um_per_pixel_x:.2f} μm/pixel')
"
```

---

## Further Reading

- Full guide: `docs/camera_calibration_guide.md`
- OpenCV calibration: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
- Microplastic standards: ISO 24187:2023
