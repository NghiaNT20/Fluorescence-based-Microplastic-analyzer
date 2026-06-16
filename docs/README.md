# Documentation Index

Welcome to the Microplastic Analyzer documentation! This folder contains comprehensive guides for camera calibration and size measurement.

---

## 📚 Available Documents

### 🚀 Quick Start

**[calibration_quick_reference.md](calibration_quick_reference.md)**
- **Purpose:** Fast reference for day-to-day use
- **Best for:** You know what you're doing and need quick formulas
- **Length:** 2 pages
- **Topics:** 3-step calibration, common formulas, integration examples

---

### 📖 Complete Guides

**[camera_calibration_guide.md](camera_calibration_guide.md)**
- **Purpose:** Comprehensive calibration documentation
- **Best for:** First-time setup, understanding concepts
- **Length:** 15 pages
- **Topics:** 
  - Three calibration methods (reference object, theoretical, OpenCV)
  - Integration with analyzer
  - Best practices
  - Troubleshooting
  - Python implementation

**[calibration_tutorial.md](calibration_tutorial.md)**
- **Purpose:** Step-by-step hands-on tutorial
- **Best for:** Learning by doing
- **Length:** 10 pages
- **Topics:**
  - 5 practical tutorials
  - Code examples you can run
  - Validation procedures
  - Real-world examples

**[calibration_math_reference.md](calibration_math_reference.md)**
- **Purpose:** Mathematical foundations
- **Best for:** Understanding the theory, error analysis
- **Length:** 12 pages
- **Topics:**
  - All formulas with derivations
  - Your camera's specific calculations
  - Uncertainty propagation
  - Resolution limits

---

## 🎯 Which Document Should I Read?

### "I just need to calibrate quickly"
→ Start with **[calibration_quick_reference.md](calibration_quick_reference.md)**

### "I've never done camera calibration before"
→ Start with **[calibration_tutorial.md](calibration_tutorial.md)**, then **[camera_calibration_guide.md](camera_calibration_guide.md)**

### "I want to understand the math and theory"
→ Read **[calibration_math_reference.md](calibration_math_reference.md)**

### "I need to integrate calibration into my code"
→ Check **[camera_calibration_guide.md](camera_calibration_guide.md)** Section "Integration with Your Microplastic Analyzer"

### "Something's wrong with my calibration"
→ See **[camera_calibration_guide.md](camera_calibration_guide.md)** Section "Troubleshooting"

---

## 📁 Related Files in Repository

### Code Implementation
- **`src/core/calibration.py`** - Main calibration module
- **`config/constants.py`** - Shape thresholds (can add size thresholds here)
- **`config/settings.py`** - Analysis parameters

### Usage Examples
```python
# In your Python code
from src.core.calibration import CameraCalibration

# Quick calibration
calib = CameraCalibration()
calib.calibrate_from_reference(100, 40)  # 100 μm reference, 40 pixels
calib.save_calibration('calibration.json')
```

### Data Files
- **`calibration.json`** - Saved calibration data (created after first calibration)

---

## 🔬 Your Camera Setup Summary

Based on your imaging system:

```
┌─────────────────────────────────────┐
│  Camera Configuration               │
├─────────────────────────────────────┤
│ Resolution:      3840 × 2160 px     │
│ Pixel Size:      1.45 μm × 1.45 μm  │
│ Sensor:          1/2.5" (5.76mm)    │
│ FOV:             94.5° diagonal      │
│ Working Dist.:   5mm (water layer)  │
│ Target Range:    10-100 μm          │
└─────────────────────────────────────┘

Expected Calibration: ~2.5 μm/pixel
Minimum Detectable:   ~7.5 μm
```

---

## 📊 Calibration Workflow Overview

```
1. Prepare Reference
   └─ Place 100 μm bead in water layer

2. Capture & Measure
   └─ Measure reference size in pixels

3. Calculate Calibration
   └─ 100 μm / measured_pixels = μm/pixel

4. Validate
   └─ Test with different known-size object

5. Save & Use
   └─ Save to calibration.json
   └─ Use in your analysis pipeline
```

---

## 🛠️ Quick Commands

### Run Calibration Demo
```bash
python src/core/calibration.py
```

### Create Calibration File (Theoretical)
```bash
python -c "from src.core.calibration import CameraCalibration; \
c = CameraCalibration(); \
c.calibrate_theoretical(5.03, 94.5, 5.0, 3840); \
c.save_calibration('calibration.json')"
```

### Test Existing Calibration
```bash
python -c "from src.core.calibration import CameraCalibration; \
c = CameraCalibration(); \
c.load_calibration('calibration.json'); \
print(f'100 pixels = {c.pixel_length_to_um(100):.1f} μm')"
```

---

## 📝 Document Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-04-08 | 1.0 | Initial documentation set created |
|  |  | - Complete calibration guide |
|  |  | - Step-by-step tutorial |
|  |  | - Mathematical reference |
|  |  | - Quick reference card |

---

## 🆘 Getting Help

### Common Issues
1. **"My calibration varies across the image"**
   - Lens distortion → See [camera_calibration_guide.md](camera_calibration_guide.md#troubleshooting)

2. **"Small particles aren't accurate"**
   - Resolution limit → See [calibration_math_reference.md](calibration_math_reference.md#resolution--detection-limits)

3. **"I don't have a calibration reference"**
   - Use theoretical calibration → See [calibration_tutorial.md](calibration_tutorial.md#tutorial-2-theoretical-calibration-no-reference)

### Finding Information
- **Search tip:** Use Ctrl+F to search within documents
- **Example lookup:** Search for "100 μm" to find relevant examples
- **Formula lookup:** Check [calibration_math_reference.md](calibration_math_reference.md)

---

## 📚 Additional Resources

### External Documentation
- **OpenCV Calibration:** https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
- **NumPy Documentation:** https://numpy.org/doc/
- **scikit-image regionprops:** https://scikit-image.org/docs/stable/api/skimage.measure.html

### Standards & References
- **ISO 24187:2023** - Microplastics measurement guidelines
- **Hidalgo-Ruz et al. (2012)** - Microplastics in marine environment review

### Calibration Targets
- Edmund Optics: Precision calibration slides
- Thorlabs: Resolution targets
- Stage micrometers: Various suppliers

---

## 🔄 Staying Updated

As you use the calibration system:
1. **Document your findings** - Add notes to this folder
2. **Track calibration history** - Keep dated calibration files
3. **Validate regularly** - Monthly calibration checks
4. **Report issues** - If you find errors in documentation

---

## 📖 Reading Order for Beginners

Recommended sequence for first-time users:

1. **Start:** [calibration_quick_reference.md](calibration_quick_reference.md) (5 min)
   - Get overview of what's involved

2. **Learn:** [calibration_tutorial.md](calibration_tutorial.md) (30 min)
   - Follow Tutorial 1 or 2
   - Actually calibrate your system

3. **Understand:** [camera_calibration_guide.md](camera_calibration_guide.md) (45 min)
   - Read sections relevant to your method
   - Keep as reference for later

4. **Deep Dive:** [calibration_math_reference.md](calibration_math_reference.md) (optional)
   - When you need to understand the math
   - For troubleshooting accuracy issues

---

## ✅ Learning Checklist

Track your progress:

- [ ] Read quick reference
- [ ] Understand calibration concept
- [ ] Have reference object ready
- [ ] Completed first calibration
- [ ] Validated calibration accuracy
- [ ] Saved calibration file
- [ ] Integrated into analysis code
- [ ] Tested with real samples
- [ ] Documented your setup

---

**Questions or issues?** Check the troubleshooting sections or search within the documents for specific topics.

**Ready to start?** → [calibration_quick_reference.md](calibration_quick_reference.md)
