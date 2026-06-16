# Mathematical Reference: Camera Size Calculations

## Core Concepts

### 1. Pixel-to-Real-World Relationship

The fundamental equation for converting pixel measurements to physical size:

```
Real Size (μm) = Pixel Size × Calibration Factor (μm/pixel)
```

---

## Key Formulas

### Area Conversion

**Pixel Area → Real Area:**
$$
\text{Area}_{\mu m^2} = \text{Area}_{pixels} \times \left(\frac{\mu m}{pixel}\right)^2
$$

**Example:**
- Particle area: 500 pixels²
- Calibration: 2.5 μm/pixel
- Real area: $500 \times (2.5)^2 = 3125$ μm²

---

### Diameter Calculation

**Equivalent Circular Diameter:**
$$
d = 2 \times \sqrt{\frac{A}{\pi}}
$$

Where:
- $d$ = diameter (μm)
- $A$ = area (μm²)

**From Pixel Area Directly:**
$$
d_{\mu m} = 2 \times \sqrt{\frac{\text{Area}_{pixels} \times \left(\frac{\mu m}{pixel}\right)^2}{\pi}}
$$

**Example:**
- Particle area: 500 pixels²
- Calibration: 2.5 μm/pixel
- Diameter: $2 \times \sqrt{\frac{3125}{\pi}} = 63.1$ μm

---

### Calibration Factor

**From Reference Object:**
$$
\frac{\mu m}{pixel} = \frac{\text{Known Size}_{(\mu m)}}{\text{Measured Size}_{(pixels)}}
$$

**Example:**
- 100 μm reference measures 40 pixels
- Calibration: $\frac{100}{40} = 2.5$ μm/pixel

**Inverse (Pixels per Micrometer):**
$$
\frac{pixels}{\mu m} = \frac{\text{Measured Size}_{(pixels)}}{\text{Known Size}_{(\mu m)}}
$$

---

### Field of View Calculation

**From Sensor and Lens Properties:**

**Focal Length:**
$$
f = \frac{d_{sensor}}{2 \times \tan\left(\frac{FOV}{2}\right)}
$$

Where:
- $f$ = focal length (mm)
- $d_{sensor}$ = sensor diagonal (mm)
- $FOV$ = field of view diagonal (degrees)

**FOV Width at Working Distance:**
$$
W_{FOV} = \frac{w_{sensor} \times D}{f}
$$

Where:
- $W_{FOV}$ = field of view width (mm)
- $w_{sensor}$ = sensor width (mm)
- $D$ = working distance (mm)
- $f$ = focal length (mm)

**Calibration from FOV:**
$$
\frac{\mu m}{pixel} = \frac{W_{FOV} \times 1000}{W_{resolution}}
$$

Where:
- $W_{FOV}$ = FOV width (mm)
- $W_{resolution}$ = image width (pixels)

---

## Your Camera Setup Calculations

### Given Specifications

```
Sensor: 1/2.5" (5.76 mm diagonal)
Resolution: 3840 × 2160 pixels
Pixel Size: 1.45 μm × 1.45 μm (physical sensor pixel)
FOV: 94.5° diagonal
Working Distance: 5 mm
Aspect Ratio: 16:9
```

### Step-by-Step Calculation

**1. Calculate Sensor Dimensions:**
$$
w_{sensor} = \frac{5.76 \times 16}{\sqrt{16^2 + 9^2}} = 5.03 \text{ mm}
$$

$$
h_{sensor} = \frac{5.76 \times 9}{\sqrt{16^2 + 9^2}} = 2.83 \text{ mm}
$$

**2. Calculate Focal Length:**
$$
f = \frac{5.76}{2 \times \tan\left(\frac{94.5°}{2}\right)} = \frac{5.76}{2 \times \tan(47.25°)} = \frac{5.76}{2.169} = 2.66 \text{ mm}
$$

**3. Calculate FOV at 5mm Working Distance:**
$$
W_{FOV} = \frac{5.03 \times 5}{2.66} = 9.45 \text{ mm}
$$

$$
H_{FOV} = \frac{2.83 \times 5}{2.66} = 5.32 \text{ mm}
$$

**4. Calculate Calibration Factor:**
$$
\frac{\mu m}{pixel}_x = \frac{9.45 \times 1000}{3840} = 2.46 \text{ μm/pixel}
$$

$$
\frac{\mu m}{pixel}_y = \frac{5.32 \times 1000}{2160} = 2.46 \text{ μm/pixel}
$$

### Theoretical Results

```
FOV: 9.45 × 5.32 mm
Calibration: 2.46 μm/pixel
Minimum detectable: ~7.4 μm (3 pixels)
```

---

## Magnification Calculations

### Optical Magnification

$$
M = \frac{\text{Image Size}}{\text{Object Size}}
$$

**For your setup:**
$$
M = \frac{w_{sensor}}{W_{FOV}} = \frac{5.03 \text{ mm}}{9.45 \text{ mm}} = 0.53\times
$$

This is a demagnifying system (M < 1), which increases FOV.

### Digital Magnification

$$
M_{digital} = \frac{\text{Sensor Pixel Size}}{\text{Effective Pixel Size}}
$$

$$
M_{digital} = \frac{1.45 \text{ μm}}{2.46 \text{ μm}} = 0.59\times
$$

### Total System Magnification

$$
M_{total} = M_{optical} \times M_{digital} = 0.53 \times 0.59 = 0.31\times
$$

---

## Resolution & Detection Limits

### Nyquist-Shannon Sampling Theorem

Minimum feature size that can be resolved:

$$
d_{min} = 2 \times \frac{\mu m}{pixel}
$$

For your system:
$$
d_{min} = 2 \times 2.46 = 4.92 \text{ μm}
$$

### Practical Detection Limit

In practice, need 3-5 pixels for reliable detection:

$$
d_{practical} = (3 \text{ to } 5) \times \frac{\mu m}{pixel}
$$

For your system:
$$
d_{practical} = 3 \times 2.46 = 7.4 \text{ μm (minimum)}
$$
$$
d_{practical} = 5 \times 2.46 = 12.3 \text{ μm (recommended)}
$$

**Your 10-100 μm target range:**
- 10 μm ≈ 4 pixels (marginal)
- 20 μm ≈ 8 pixels (good)
- 50 μm ≈ 20 pixels (excellent)
- 100 μm ≈ 41 pixels (excellent)

---

## Uncertainty & Error Propagation

### Calibration Uncertainty

For a single reference measurement:

$$
\sigma_{calib} = \frac{\mu m}{pixel} \times \sqrt{\left(\frac{\sigma_{ref}}{ref}\right)^2 + \left(\frac{\sigma_{meas}}{meas}\right)^2}
$$

Where:
- $\sigma_{calib}$ = calibration uncertainty
- $\sigma_{ref}$ = reference size uncertainty
- $\sigma_{meas}$ = measurement uncertainty

**Example:**
- Reference: 100 ± 1 μm (1% uncertainty)
- Measurement: 40 ± 0.5 pixels (1.25% uncertainty)
- Calibration: 2.5 ± ? μm/pixel

$$
\sigma_{calib} = 2.5 \times \sqrt{(0.01)^2 + (0.0125)^2} = 2.5 \times 0.016 = 0.04
$$

**Result:** 2.5 ± 0.04 μm/pixel (1.6% uncertainty)

### Area Measurement Uncertainty

$$
\sigma_{area} = \text{Area} \times 2 \times \frac{\sigma_{calib}}{calib}
$$

Factor of 2 because area uses (μm/pixel)²

**Example:**
- Measured area: 500 ± 10 pixels² (2% measurement error)
- Calibration: 2.5 ± 0.04 μm/pixel (1.6% calibration error)

$$
\sigma_{total} = \sqrt{(2\%)^2 + 2 \times (1.6\%)^2} = \sqrt{4 + 10.24} = 3.77\%
$$

**Result for 3125 μm²:** ±118 μm² (3.8% total uncertainty)

---

## Water Refraction Effects

### Snell's Law

$$
n_1 \sin(\theta_1) = n_2 \sin(\theta_2)
$$

Where:
- $n_1$ = refractive index of air (1.00)
- $n_2$ = refractive index of water (1.33)
- $\theta$ = angle of incidence/refraction

### Apparent Size Change

Objects viewed through water appear:

$$
\text{Apparent Size} = \text{Real Size} \times \frac{n_{water}}{n_{air}} = \text{Real Size} \times 1.33
$$

**Important:** If calibrating through water with reference objects also in water, this cancels out! No correction needed if setup is consistent.

---

## Geometric Relationships

### Aspect Ratio

$$
\text{Aspect Ratio} = \frac{\text{Major Axis}}{\text{Minor Axis}}
$$

### Circularity

$$
C = \frac{4\pi A}{P^2}
$$

Where:
- $C$ = circularity (1.0 = perfect circle)
- $A$ = area
- $P$ = perimeter

### Eccentricity

$$
e = \sqrt{1 - \frac{b^2}{a^2}}
$$

Where:
- $e$ = eccentricity (0 = circle, 1 = line)
- $a$ = major axis length
- $b$ = minor axis length

---

## Quick Reference Table

| Calculation | Formula | Example (500 px², 2.5 μm/px) |
|-------------|---------|------------------------------|
| **Area** | $A_{pixels} \times (μm/px)^2$ | $500 \times 2.5^2 = 3125$ μm² |
| **Diameter** | $2\sqrt{A/\pi}$ | $2\sqrt{3125/\pi} = 63.1$ μm |
| **Perimeter** | $P_{pixels} \times (μm/px)$ | $80 \times 2.5 = 200$ μm |
| **Calibration** | $size_{known} / size_{measured}$ | $100 / 40 = 2.5$ μm/px |
| **Min Size** | $3 \times (μm/px)$ | $3 \times 2.5 = 7.5$ μm |

---

## Python Implementation Examples

### Basic Calculations

```python
import numpy as np

# Constants
um_per_pixel = 2.5

# Area conversion
area_px = 500
area_um2 = area_px * (um_per_pixel ** 2)  # 3125 μm²

# Diameter from area
diameter_um = 2 * np.sqrt(area_um2 / np.pi)  # 63.1 μm

# Length conversion
perimeter_px = 80
perimeter_um = perimeter_px * um_per_pixel  # 200 μm
```

### FOV Calculation

```python
import math

sensor_width_mm = 5.03
fov_degrees = 94.5
working_distance_mm = 5.0
resolution_width_px = 3840

# Calculate focal length
sensor_diagonal_mm = 5.76
focal_length_mm = sensor_diagonal_mm / (2 * math.tan(math.radians(fov_degrees / 2)))

# Calculate FOV
fov_width_mm = (sensor_width_mm * working_distance_mm) / focal_length_mm

# Calculate calibration
um_per_pixel = (fov_width_mm * 1000) / resolution_width_px

print(f"Calibration: {um_per_pixel:.3f} μm/pixel")
```

### Uncertainty Propagation

```python
import numpy as np

# Reference measurement with uncertainty
ref_size_um = 100.0
ref_uncertainty_um = 1.0  # ±1 μm

measured_px = 40.0
measured_uncertainty_px = 0.5  # ±0.5 pixels

# Calculate calibration
calib = ref_size_um / measured_px

# Calculate uncertainty
rel_error_ref = ref_uncertainty_um / ref_size_um
rel_error_meas = measured_uncertainty_px / measured_px
total_rel_error = np.sqrt(rel_error_ref**2 + rel_error_meas**2)

calib_uncertainty = calib * total_rel_error

print(f"Calibration: {calib:.3f} ± {calib_uncertainty:.3f} μm/pixel")
print(f"Relative error: {total_rel_error*100:.2f}%")
```

---

## Glossary

- **FOV (Field of View):** The extent of the observable area
- **Working Distance:** Distance from lens to sample plane
- **Pixel Size:** Physical size of camera sensor pixel
- **Calibration Factor:** Conversion from pixels to real units
- **Equivalent Diameter:** Diameter of circle with same area
- **Resolution Limit:** Minimum feature size that can be detected

---

## References

1. **Optics:**
   - Hecht, E. "Optics" (5th ed.)
   - Smith, W. J. "Modern Optical Engineering"

2. **Image Processing:**
   - Gonzalez & Woods "Digital Image Processing"
   - Russ, J.C. "The Image Processing Handbook"

3. **Metrology:**
   - ISO/IEC Guide 98-3:2008 (Uncertainty of measurement)
   - JCGM 100:2008 (GUM)

4. **Microplastic Analysis:**
   - Hidalgo-Ruz et al. (2012) Marine Environmental Research
   - ISO 24187:2023 (Microplastics measurement)

---

## Useful Conversions

| Unit | Conversion |
|------|------------|
| 1 mm | 1000 μm |
| 1 μm | 0.001 mm |
| 1 μm | 1000 nm |
| 1" sensor | ~16 mm diagonal |
| 1/2.5" sensor | 5.76 mm diagonal |
| 1/3" sensor | 6.0 mm diagonal |

---

For practical implementation, see:
- `src/core/calibration.py` - Python implementation
- `docs/calibration_tutorial.md` - Step-by-step guide
- `docs/calibration_quick_reference.md` - Quick lookup
