"""
Camera Calibration Dialog for Microplastic Analyzer
Allows users to input camera parameters and calculate calibration
"""

import math
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, 
                             QComboBox, QDoubleSpinBox, QSpinBox, QTextEdit,
                             QMessageBox, QTabWidget, QWidget, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from src.core.calibration import CameraCalibration


class CameraCalibrationDialog(QDialog):
    """Dialog for camera calibration with parameter-based and reference-based methods"""
    
    calibration_changed = pyqtSignal(object)  # Emits CameraCalibration object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.calibration = CameraCalibration()
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle("Camera Calibration - Size Measurement Setup")
        self.setGeometry(150, 150, 800, 700)
        
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📐 Camera Calibration for Size Measurement")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create tabs for different calibration methods
        self.tabs = QTabWidget()
        
        # Tab 1: Parameter-based calibration
        self.tab_params = self.create_parameter_tab()
        self.tabs.addTab(self.tab_params, "📷 Camera Parameters")
        
        # Tab 2: Reference object calibration
        self.tab_reference = self.create_reference_tab()
        self.tabs.addTab(self.tab_reference, "📏 Reference Object")
        
        # Tab 3: Results and help
        self.tab_results = self.create_results_tab()
        self.tabs.addTab(self.tab_results, "📊 Results & Info")
        
        main_layout.addWidget(self.tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("📂 Load Calibration")
        self.load_btn.clicked.connect(self.load_calibration)
        button_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("💾 Save Calibration")
        self.save_btn.clicked.connect(self.save_calibration)
        button_layout.addWidget(self.save_btn)
        
        button_layout.addStretch()
        
        self.apply_btn = QPushButton("✓ Apply & Close")
        self.apply_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.apply_btn.clicked.connect(self.apply_calibration)
        button_layout.addWidget(self.apply_btn)
        
        self.cancel_btn = QPushButton("✗ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
    def create_parameter_tab(self):
        """Create tab for parameter-based calibration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel(
            "Calculate calibration from camera specifications.\n"
            "Enter your camera and lens parameters below:"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #E3F2FD; padding: 10px; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Parameter input group
        param_group = QGroupBox("Camera Specifications")
        param_layout = QGridLayout()
        
        # Row 0: Sensor size
        param_layout.addWidget(QLabel("Sensor Size:"), 0, 0)
        self.sensor_combo = QComboBox()
        self.sensor_combo.addItems([
            '1/2.5" (5.76mm diagonal)',
            '1/3" (6.00mm diagonal)',
            '1/2.3" (7.66mm diagonal)',
            '1/1.7" (9.50mm diagonal)',
            'Custom'
        ])
        self.sensor_combo.setCurrentIndex(0)
        self.sensor_combo.currentIndexChanged.connect(self.on_sensor_changed)
        param_layout.addWidget(self.sensor_combo, 0, 1, 1, 2)
        
        # Custom sensor diagonal
        param_layout.addWidget(QLabel("Custom Diagonal (mm):"), 0, 3)
        self.sensor_diagonal = QDoubleSpinBox()
        self.sensor_diagonal.setRange(1.0, 50.0)
        self.sensor_diagonal.setValue(5.76)
        self.sensor_diagonal.setDecimals(2)
        self.sensor_diagonal.setSingleStep(0.1)
        self.sensor_diagonal.setEnabled(False)
        param_layout.addWidget(self.sensor_diagonal, 0, 4)
        
        # Row 1: Resolution
        param_layout.addWidget(QLabel("Resolution (Width):"), 1, 0)
        self.resolution_width = QSpinBox()
        self.resolution_width.setRange(100, 10000)
        self.resolution_width.setValue(3840)
        self.resolution_width.setSuffix(" px")
        param_layout.addWidget(self.resolution_width, 1, 1)
        
        param_layout.addWidget(QLabel("Aspect Ratio:"), 1, 2)
        self.aspect_ratio = QComboBox()
        self.aspect_ratio.addItems(['16:9', '4:3', '1:1', 'Custom'])
        param_layout.addWidget(self.aspect_ratio, 1, 3)
        
        self.aspect_custom = QDoubleSpinBox()
        self.aspect_custom.setRange(0.1, 10.0)
        self.aspect_custom.setValue(1.778)  # 16/9
        self.aspect_custom.setDecimals(3)
        self.aspect_custom.setEnabled(False)
        param_layout.addWidget(self.aspect_custom, 1, 4)
        self.aspect_ratio.currentTextChanged.connect(self.on_aspect_changed)
        
        # Row 2: Field of View
        param_layout.addWidget(QLabel("Field of View:"), 2, 0)
        self.fov_degrees = QDoubleSpinBox()
        self.fov_degrees.setRange(10.0, 180.0)
        self.fov_degrees.setValue(94.5)
        self.fov_degrees.setDecimals(1)
        self.fov_degrees.setSuffix(" °")
        self.fov_degrees.setToolTip("Diagonal field of view in degrees")
        param_layout.addWidget(self.fov_degrees, 2, 1)
        
        # Row 3: Focal Length
        param_layout.addWidget(QLabel("Focal Length:"), 3, 0)
        self.focal_length = QDoubleSpinBox()
        self.focal_length.setRange(0.1, 500.0)
        self.focal_length.setValue(2.8)
        self.focal_length.setDecimals(2)
        self.focal_length.setSuffix(" mm")
        self.focal_length.setToolTip("Lens focal length (e.g., 2.1, 2.8, 3.6 mm)")
        param_layout.addWidget(self.focal_length, 3, 1)
        
        # Preset focal lengths
        param_layout.addWidget(QLabel("Preset:"), 3, 2)
        focal_preset = QComboBox()
        focal_preset.addItems(['Custom', '2.1 mm', '2.8 mm', '3.6 mm', '5.0 mm', '8.0 mm'])
        focal_preset.currentTextChanged.connect(self.on_focal_preset_changed)
        param_layout.addWidget(focal_preset, 3, 3, 1, 2)
        
        # Row 4: Working Distance
        param_layout.addWidget(QLabel("Working Distance:"), 4, 0)
        self.working_distance = QDoubleSpinBox()
        self.working_distance.setRange(0.1, 1000.0)
        self.working_distance.setValue(5.0)
        self.working_distance.setDecimals(2)
        self.working_distance.setSuffix(" mm")
        self.working_distance.setToolTip("Distance from camera lens to object (e.g., water layer depth)")
        param_layout.addWidget(self.working_distance, 4, 1)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Calculate button
        calc_btn = QPushButton("🔍 Calculate Calibration")
        calc_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        calc_btn.clicked.connect(self.calculate_from_parameters)
        layout.addWidget(calc_btn)
        
        # Results display
        self.param_results = QTextEdit()
        self.param_results.setReadOnly(True)
        self.param_results.setMaximumHeight(200)
        self.param_results.setPlaceholderText("Calibration results will appear here...")
        layout.addWidget(self.param_results)
        
        layout.addStretch()
        return widget
    
    def create_reference_tab(self):
        """Create tab for reference object calibration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel(
            "Calibrate using a known-size reference object.\n"
            "1. Place reference object (e.g., 100 μm bead) in view\n"
            "2. Measure its size in pixels using your image\n"
            "3. Enter values below"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #FFF3E0; padding: 10px; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Reference input group
        ref_group = QGroupBox("Reference Object Measurement")
        ref_layout = QFormLayout()
        
        # Known size
        self.ref_size = QDoubleSpinBox()
        self.ref_size.setRange(0.1, 100000.0)
        self.ref_size.setValue(100.0)
        self.ref_size.setDecimals(2)
        self.ref_size.setSuffix(" μm")
        self.ref_size.setToolTip("Known size of reference object in micrometers")
        ref_layout.addRow("Known Size:", self.ref_size)
        
        # Common references preset
        ref_preset = QComboBox()
        ref_preset.addItems([
            'Custom',
            '25 μm bead',
            '50 μm bead',
            '100 μm bead',
            '200 μm bead',
            '500 μm (0.5 mm)',
            '1000 μm (1 mm)'
        ])
        ref_preset.currentTextChanged.connect(self.on_ref_preset_changed)
        ref_layout.addRow("Common Sizes:", ref_preset)
        
        # Measured size in pixels
        self.ref_pixels = QDoubleSpinBox()
        self.ref_pixels.setRange(1.0, 100000.0)
        self.ref_pixels.setValue(40.0)
        self.ref_pixels.setDecimals(1)
        self.ref_pixels.setSuffix(" pixels")
        self.ref_pixels.setToolTip("Measured size of reference in pixels\n(diameter, width, or length)")
        ref_layout.addRow("Measured Size:", self.ref_pixels)
        
        ref_group.setLayout(ref_layout)
        layout.addWidget(ref_group)
        
        # Calculate button
        calc_btn = QPushButton("🔍 Calculate from Reference")
        calc_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px;")
        calc_btn.clicked.connect(self.calculate_from_reference)
        layout.addWidget(calc_btn)
        
        # Results display
        self.ref_results = QTextEdit()
        self.ref_results.setReadOnly(True)
        self.ref_results.setMaximumHeight(200)
        self.ref_results.setPlaceholderText("Calibration results will appear here...")
        layout.addWidget(self.ref_results)
        
        # Validation section
        val_group = QGroupBox("Validate Calibration")
        val_layout = QFormLayout()
        
        self.test_pixels = QDoubleSpinBox()
        self.test_pixels.setRange(1.0, 100000.0)
        self.test_pixels.setValue(20.0)
        self.test_pixels.setDecimals(1)
        self.test_pixels.setSuffix(" pixels")
        val_layout.addRow("Test Object (pixels):", self.test_pixels)
        
        self.test_result = QLineEdit()
        self.test_result.setReadOnly(True)
        self.test_result.setPlaceholderText("Predicted size will appear here")
        val_layout.addRow("Predicted Size (μm):", self.test_result)
        
        test_btn = QPushButton("Test Conversion")
        test_btn.clicked.connect(self.test_conversion)
        val_layout.addRow("", test_btn)
        
        val_group.setLayout(val_layout)
        layout.addWidget(val_group)
        
        layout.addStretch()
        return widget
    
    def create_results_tab(self):
        """Create tab showing results and help information"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Current calibration status
        status_group = QGroupBox("Current Calibration Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("⚠ Not calibrated")
        self.status_label.setStyleSheet("font-size: 12pt; color: #F44336;")
        status_layout.addWidget(self.status_label)
        
        self.calib_info = QTextEdit()
        self.calib_info.setReadOnly(True)
        self.calib_info.setMaximumHeight(120)
        self.calib_info.setPlaceholderText("No calibration data available")
        status_layout.addWidget(self.calib_info)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Help information
        help_group = QGroupBox("Quick Reference")
        help_layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
            <h3>How to Calibrate:</h3>
            <p><b>Method 1: Camera Parameters</b> (Theoretical)</p>
            <ul>
                <li>Input your camera specifications (sensor, FOV, focal length)</li>
                <li>Specify working distance (camera to object)</li>
                <li>Click "Calculate Calibration"</li>
                <li>Accuracy: ±10-15%</li>
            </ul>
            
            <p><b>Method 2: Reference Object</b> (Recommended)</p>
            <ul>
                <li>Place known-size object (e.g., 100 μm bead) in view</li>
                <li>Measure its size in pixels in your image</li>
                <li>Enter known size and measured pixels</li>
                <li>Click "Calculate from Reference"</li>
                <li>Accuracy: ±3-5%</li>
            </ul>
            
            <h3>Understanding Results:</h3>
            <p><b>μm/pixel:</b> How many micrometers each pixel represents</p>
            <p><b>Field of View:</b> Total area visible in camera</p>
            <p><b>Min Detectable Size:</b> Smallest particle reliably measured (typically 3-5 pixels)</p>
            
            <h3>Tips:</h3>
            <ul>
                <li>Always calibrate with reference object for best accuracy</li>
                <li>Keep working distance constant</li>
                <li>Recalibrate if you change focus or zoom</li>
                <li>Save calibration after setup</li>
            </ul>
        """)
        help_layout.addWidget(help_text)
        
        help_group.setLayout(help_layout)
        layout.addWidget(help_group)
        
        return widget
    
    def on_sensor_changed(self, index):
        """Handle sensor size selection"""
        sensor_sizes = {
            0: 5.76,  # 1/2.5"
            1: 6.00,  # 1/3"
            2: 7.66,  # 1/2.3"
            3: 9.50,  # 1/1.7"
        }
        
        if index in sensor_sizes:
            self.sensor_diagonal.setValue(sensor_sizes[index])
            self.sensor_diagonal.setEnabled(False)
        else:
            self.sensor_diagonal.setEnabled(True)
    
    def on_aspect_changed(self, text):
        """Handle aspect ratio selection"""
        aspect_ratios = {
            '16:9': 16/9,
            '4:3': 4/3,
            '1:1': 1.0
        }
        
        if text in aspect_ratios:
            self.aspect_custom.setValue(aspect_ratios[text])
            self.aspect_custom.setEnabled(False)
        else:
            self.aspect_custom.setEnabled(True)
    
    def on_focal_preset_changed(self, text):
        """Handle focal length preset"""
        if text != 'Custom':
            value = float(text.split()[0])
            self.focal_length.setValue(value)
    
    def on_ref_preset_changed(self, text):
        """Handle reference size preset"""
        ref_sizes = {
            '25 μm bead': 25.0,
            '50 μm bead': 50.0,
            '100 μm bead': 100.0,
            '200 μm bead': 200.0,
            '500 μm (0.5 mm)': 500.0,
            '1000 μm (1 mm)': 1000.0
        }
        
        if text in ref_sizes:
            self.ref_size.setValue(ref_sizes[text])
    
    def calculate_from_parameters(self):
        """Calculate calibration from camera parameters"""
        try:
            # Get parameters
            sensor_diagonal_mm = self.sensor_diagonal.value()
            resolution_width = self.resolution_width.value()
            aspect = self.aspect_custom.value()
            focal_length_mm = self.focal_length.value()
            working_distance_mm = self.working_distance.value()
            
            # Calculate sensor dimensions
            sensor_width_mm = sensor_diagonal_mm * math.sqrt(aspect**2 / (aspect**2 + 1))
            sensor_height_mm = sensor_width_mm / aspect
            
            # Calculate field of view at working distance
            fov_width_mm = (sensor_width_mm * working_distance_mm) / focal_length_mm
            fov_height_mm = (sensor_height_mm * working_distance_mm) / focal_length_mm
            
            # Calculate resolution
            resolution_height = int(resolution_width / aspect)
            
            # Calculate calibration
            um_per_pixel_x = (fov_width_mm * 1000) / resolution_width
            um_per_pixel_y = (fov_height_mm * 1000) / resolution_height
            
            # Update calibration object
            self.calibration = CameraCalibration((um_per_pixel_x, um_per_pixel_y))
            
            # Display results
            results = f"""
✓ Calibration Calculated Successfully!

Sensor Dimensions: {sensor_width_mm:.2f} × {sensor_height_mm:.2f} mm
Focal Length: {focal_length_mm} mm
Working Distance: {working_distance_mm} mm

Field of View: {fov_width_mm:.2f} × {fov_height_mm:.2f} mm
            = {fov_width_mm*1000:.0f} × {fov_height_mm*1000:.0f} μm

Resolution: {resolution_width} × {resolution_height} pixels

Calibration Factor:
  X-axis: {um_per_pixel_x:.3f} μm/pixel
  Y-axis: {um_per_pixel_y:.3f} μm/pixel

Minimum Detectable Size: {3 * um_per_pixel_x:.1f} μm (3 pixels)

Your 10-100 μm particles:
  10 μm  → {10/um_per_pixel_x:.1f} pixels diameter
  50 μm  → {50/um_per_pixel_x:.1f} pixels diameter
  100 μm → {100/um_per_pixel_x:.1f} pixels diameter
"""
            self.param_results.setText(results)
            self.update_status()
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Error calculating calibration:\n{str(e)}")
    
    def calculate_from_reference(self):
        """Calculate calibration from reference object"""
        try:
            ref_size_um = self.ref_size.value()
            ref_pixels = self.ref_pixels.value()
            
            if ref_pixels <= 0:
                QMessageBox.warning(self, "Invalid Input", "Measured size must be greater than 0 pixels")
                return
            
            # Calculate calibration
            self.calibration = CameraCalibration()
            self.calibration.calibrate_from_reference(ref_size_um, ref_pixels)
            
            um_per_pixel = self.calibration.um_per_pixel_x
            
            # Display results
            results = f"""
✓ Calibration from Reference Object!

Reference Object:
  Known Size: {ref_size_um} μm
  Measured: {ref_pixels} pixels

Calibration Factor: {um_per_pixel:.3f} μm/pixel

Minimum Detectable Size: {3 * um_per_pixel:.1f} μm (3 pixels)

Example Conversions:
  10 μm  = {10/um_per_pixel:.1f} pixels
  50 μm  = {50/um_per_pixel:.1f} pixels
  100 μm = {100/um_per_pixel:.1f} pixels
  
  100 pixels = {100 * um_per_pixel:.1f} μm
  500 pixels = {500 * um_per_pixel:.1f} μm

Size Categories:
  <10 μm    → Nanoplastic ({10/um_per_pixel:.1f} px)
  10-100 μm → Microplastic ({10/um_per_pixel:.1f}-{100/um_per_pixel:.1f} px)
  >100 μm   → Large particles (>{100/um_per_pixel:.1f} px)
"""
            self.ref_results.setText(results)
            self.update_status()
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Error calculating calibration:\n{str(e)}")
    
    def test_conversion(self):
        """Test conversion with calibration"""
        if not self.calibration.is_calibrated:
            QMessageBox.warning(self, "Not Calibrated", "Please calculate calibration first")
            return
        
        pixels = self.test_pixels.value()
        size_um = self.calibration.pixel_length_to_um(pixels)
        self.test_result.setText(f"{size_um:.2f} μm")
    
    def update_status(self):
        """Update calibration status display"""
        if self.calibration.is_calibrated:
            self.status_label.setText("✓ Calibrated")
            self.status_label.setStyleSheet("font-size: 12pt; color: #4CAF50;")
            
            info = f"""
Calibration Factor:
  X-axis: {self.calibration.um_per_pixel_x:.3f} μm/pixel
  Y-axis: {self.calibration.um_per_pixel_y:.3f} μm/pixel

Min Detectable: {3 * self.calibration.um_per_pixel_x:.1f} μm
            """
            self.calib_info.setText(info)
        else:
            self.status_label.setText("⚠ Not calibrated")
            self.status_label.setStyleSheet("font-size: 12pt; color: #F44336;")
            self.calib_info.setPlaceholderText("No calibration data available")
    
    def save_calibration(self):
        """Save calibration to file"""
        if not self.calibration.is_calibrated:
            QMessageBox.warning(self, "Not Calibrated", "Please calculate calibration first")
            return
        
        try:
            self.calibration.save_calibration('calibration.json')
            QMessageBox.information(self, "Saved", "Calibration saved to calibration.json")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving calibration:\n{str(e)}")
    
    def load_calibration(self):
        """Load calibration from file"""
        try:
            self.calibration = CameraCalibration()
            success = self.calibration.load_calibration('calibration.json')
            if success:
                self.update_status()
                QMessageBox.information(self, "Loaded", "Calibration loaded from calibration.json")
            else:
                QMessageBox.warning(self, "Load Error", "Could not load calibration file")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Error loading calibration:\n{str(e)}")
    
    def apply_calibration(self):
        """Apply calibration and close dialog"""
        if not self.calibration.is_calibrated:
            reply = QMessageBox.question(
                self, "Not Calibrated",
                "Calibration is not set. Continue without calibration?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        self.calibration_changed.emit(self.calibration)
        self.accept()
    
    def get_calibration(self):
        """Get the calibration object"""
        return self.calibration
