import sys
import ctypes
import json
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QSlider, QPushButton, QCheckBox,
                           QGroupBox, QSpinBox, QLineEdit, QComboBox, QSystemTrayIcon, QMenu,
                           QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QSharedMemory
from PyQt5.QtCore import QLineF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QIcon

# Global hotkey support
import threading
import time

# Default configuration
DEFAULT_CONFIG = {
    'color': {'r': 0, 'g': 255, 'b': 0, 'a': 255},  # Green
    'outline_color': {'r': 0, 'g': 0, 'b': 0, 'a': 255},  # Black
    'line_thickness': 2,
    'crosshair_length': 8,
    'crosshair_gap': 2,
    'outline_enabled': True,
    'outline_thickness': 1,
    'crosshair_style': 'cross',  # 'cross' or 'dot'
    'dot_size': 6
}

# Default crosshair presets
DEFAULT_PRESETS = {
    'Default Green': {
        'color': {'r': 0, 'g': 255, 'b': 0, 'a': 255},
        'outline_color': {'r': 0, 'g': 0, 'b': 0, 'a': 255},
        'line_thickness': 2,
        'crosshair_length': 8,
        'crosshair_gap': 2,
        'outline_enabled': True,
        'outline_thickness': 1,
        'crosshair_style': 'cross',
        'dot_size': 6
    },
    'Red Dot': {
        'color': {'r': 255, 'g': 0, 'b': 0, 'a': 255},
        'outline_color': {'r': 0, 'g': 0, 'b': 0, 'a': 255},
        'line_thickness': 2,
        'crosshair_length': 0,
        'crosshair_gap': 0,
        'outline_enabled': True,
        'outline_thickness': 1,
        'crosshair_style': 'dot',
        'dot_size': 8
    },
    'Blue Cross': {
        'color': {'r': 0, 'g': 0, 'b': 255, 'a': 255},
        'outline_color': {'r': 255, 'g': 255, 'b': 255, 'a': 255},
        'line_thickness': 3,
        'crosshair_length': 12,
        'crosshair_gap': 4,
        'outline_enabled': True,
        'outline_thickness': 2,
        'crosshair_style': 'cross',
        'dot_size': 6
    },
    'White Minimal': {
        'color': {'r': 255, 'g': 255, 'b': 255, 'a': 255},
        'outline_color': {'r': 0, 'g': 0, 'b': 0, 'a': 255},
        'line_thickness': 1,
        'crosshair_length': 6,
        'crosshair_gap': 1,
        'outline_enabled': False,
        'outline_thickness': 1,
        'crosshair_style': 'cross',
        'dot_size': 6
    }
}

# Default color presets
DEFAULT_COLORS = {
    'Green': '#00FF00',
    'Red': '#FF0000',
    'Blue': '#0000FF',
    'White': '#FFFFFF',
    'Yellow': '#FFFF00',
    'Cyan': '#00FFFF',
    'Magenta': '#FF00FF',
    'Orange': '#FFA500',
    'Pink': '#FF69B4',
    'Purple': '#800080'
}

class CrosshairPresetManager:
    """Manages saving, loading, and managing multiple crosshair presets"""
    
    def __init__(self, filename='crosshair_presets.json'):
        self.filename = filename
        self.presets = self.load_presets()
    
    def load_presets(self):
        """Load presets from file, creating default presets if file doesn't exist"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    loaded_presets = json.load(f)
                    # Merge with default presets to ensure all defaults are available
                    merged_presets = DEFAULT_PRESETS.copy()
                    merged_presets.update(loaded_presets)
                    return merged_presets
            else:
                # Create file with default presets
                self.save_presets(DEFAULT_PRESETS)
                return DEFAULT_PRESETS.copy()
        except Exception as e:
            print(f"Error loading presets: {e}")
            return DEFAULT_PRESETS.copy()
    
    def save_presets(self, presets=None):
        """Save presets to file"""
        if presets is None:
            presets = self.presets
        try:
            with open(self.filename, 'w') as f:
                json.dump(presets, f, indent=2)
            self.presets = presets
            return True
        except Exception as e:
            print(f"Error saving presets: {e}")
            return False
    
    def get_preset_names(self):
        """Get list of preset names"""
        return list(self.presets.keys())
    
    def get_preset(self, name):
        """Get a specific preset by name"""
        return self.presets.get(name, DEFAULT_CONFIG.copy())
    
    def save_current_as_preset(self, name, config):
        """Save current configuration as a new preset"""
        self.presets[name] = config.copy()
        return self.save_presets()
    
    def delete_preset(self, name):
        """Delete a preset (but not default ones)"""
        if name in DEFAULT_PRESETS:
            print(f"Cannot delete default preset: {name}")
            return False
        if name in self.presets:
            del self.presets[name]
            return self.save_presets()
        return False
    
    def rename_preset(self, old_name, new_name):
        """Rename a preset"""
        if old_name in DEFAULT_PRESETS:
            print(f"Cannot rename default preset: {old_name}")
            return False
        if old_name in self.presets and new_name not in self.presets:
            self.presets[new_name] = self.presets.pop(old_name)
            return self.save_presets()
        return False

class ImprovedHotKeyListener(QThread):
    """Improved hotkey listener with better error handling"""
    hotkey_pressed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.registered_hotkeys = []
        self.setup_hotkeys()
    
    def setup_hotkeys(self):
        """Setup Windows global hotkeys with multiple fallbacks"""
        try:
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
            
            # Virtual key codes
            hotkey_combinations = [
                (1, 0, 0x71),  # F2
                (2, 2, 0x71),  # Ctrl+F2  
                (3, 0, 0x72),  # F3
                (4, 6, ord('C')),  # Ctrl+Shift+C
                (5, 0, 0x7A),  # F11
            ]
            
            for hotkey_id, modifier, vk_code in hotkey_combinations:
                try:
                    if self.user32.RegisterHotKeyW(None, hotkey_id, modifier, vk_code):
                        self.registered_hotkeys.append(hotkey_id)
                        mod_text = {0: "", 2: "Ctrl+", 6: "Ctrl+Shift+"}
                        key_text = {0x71: "F2", 0x72: "F3", ord('C'): "C", 0x7A: "F11"}
                        print(f"Registered {mod_text.get(modifier, '')}{key_text.get(vk_code, 'Key')} as toggle hotkey")
                        break
                except:
                    continue
            
            if not self.registered_hotkeys:
                print("Warning: Could not register any global hotkeys")
                
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
    
    def run(self):
        """Listen for hotkey messages"""
        try:
            msg = ctypes.wintypes.MSG()
            
            while self.running:
                result = self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                
                if result == 0 or result == -1:
                    break
                    
                if msg.message == 0x0312:  # WM_HOTKEY
                    self.hotkey_pressed.emit("toggle")
                
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
                    
        except Exception as e:
            print(f"Error in hotkey listener: {e}")
    
    def stop(self):
        """Stop the hotkey listener and cleanup"""
        self.running = False
        try:
            for hotkey_id in self.registered_hotkeys:
                self.user32.UnregisterHotKey(None, hotkey_id)
        except:
            pass
        # Post quit message to break out of GetMessage loop
        try:
            thread_id = self.kernel32.GetCurrentThreadId()
            self.user32.PostThreadMessageW(thread_id, 0x0012, 0, 0)  # WM_QUIT
        except:
            pass
        self.quit()

class CrosshairPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.config = DEFAULT_CONFIG.copy()
        
    def update_config(self, config):
        self.config = config
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(43, 43, 43))
        
        w = self.width()
        h = self.height()
        center_x = w // 2
        center_y = h // 2
        
        # Get current settings
        main_color = QColor(self.config['color']['r'], self.config['color']['g'], 
                           self.config['color']['b'], self.config['color']['a'])
        outline_color = QColor(self.config['outline_color']['r'], self.config['outline_color']['g'], 
                              self.config['outline_color']['b'], self.config['outline_color']['a'])
        
        thickness = self.config['line_thickness']
        length = self.config['crosshair_length']
        gap = self.config['crosshair_gap']
        outline_enabled = self.config['outline_enabled']
        outline_thickness = self.config['outline_thickness']
        crosshair_style = self.config.get('crosshair_style', 'cross')
        dot_size = self.config.get('dot_size', 6)
        
        if crosshair_style == 'dot':
            # Draw outline first if enabled
            if outline_enabled:
                painter.setPen(Qt.NoPen)
                painter.setBrush(outline_color)
                painter.drawEllipse(center_x - dot_size//2 - outline_thickness, center_y - dot_size//2 - outline_thickness, dot_size + 2*outline_thickness, dot_size + 2*outline_thickness)
            # Draw main dot
            painter.setPen(Qt.NoPen)
            painter.setBrush(main_color)
            painter.drawEllipse(center_x - dot_size//2, center_y - dot_size//2, dot_size, dot_size)
        else:
            # Draw outline first if enabled
            if outline_enabled:
                outline_pen = QPen(outline_color, thickness + outline_thickness * 2)
                outline_pen.setCosmetic(True)
                outline_pen.setCapStyle(Qt.FlatCap)
                outline_pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(outline_pen)
                painter.drawLine(QLineF(center_x + 0.5, center_y - length - gap + 0.5, center_x + 0.5, center_y - gap + 0.5))
                painter.drawLine(QLineF(center_x + 0.5, center_y + gap + 0.5, center_x + 0.5, center_y + length + gap + 0.5))
                painter.drawLine(QLineF(center_x - length - gap + 0.5, center_y + 0.5, center_x - gap + 0.5, center_y + 0.5))
                painter.drawLine(QLineF(center_x + gap + 0.5, center_y + 0.5, center_x + length + gap + 0.5, center_y + 0.5))
            # Draw main crosshair
            main_pen = QPen(main_color, thickness)
            main_pen.setCosmetic(True)
            main_pen.setCapStyle(Qt.FlatCap)
            main_pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(main_pen)
            painter.drawLine(QLineF(center_x + 0.5, center_y - length - gap + 0.5, center_x + 0.5, center_y - gap + 0.5))
            painter.drawLine(QLineF(center_x + 0.5, center_y + gap + 0.5, center_x + 0.5, center_y + length + gap + 0.5))
            painter.drawLine(QLineF(center_x - length - gap + 0.5, center_y + 0.5, center_x - gap + 0.5, center_y + 0.5))
            painter.drawLine(QLineF(center_x + gap + 0.5, center_y + 0.5, center_x + length + gap + 0.5, center_y + 0.5))
        # Add preview label
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawText(10, 20, "Live Preview")
        painter.end()

class HexColorWidget(QWidget):
    color_changed = pyqtSignal(dict)
    
    def __init__(self, initial_color, label_text):
        super().__init__()
        self.setup_ui(label_text)
        self.set_color(initial_color)
        
    def setup_ui(self, label_text):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(label_text))
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Presets:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Custom", "")
        for name, hex_color in DEFAULT_COLORS.items():
            self.preset_combo.addItem(name, hex_color)
        self.preset_combo.currentTextChanged.connect(self.preset_changed)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        layout.addLayout(preset_layout)
        
        hex_layout = QHBoxLayout()
        hex_layout.addWidget(QLabel("Hex:"))
        
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("#00FF00")
        self.hex_input.setMaxLength(7)
        self.hex_input.textChanged.connect(self.hex_changed)
        hex_layout.addWidget(self.hex_input)
        
        self.color_preview = QPushButton()
        self.color_preview.setFixedSize(40, 25)
        self.color_preview.setEnabled(False)
        hex_layout.addWidget(self.color_preview)
        
        layout.addLayout(hex_layout)
        self.setLayout(layout)
    
    def preset_changed(self, preset_name):
        if preset_name != "Custom":
            hex_color = self.preset_combo.currentData()
            if hex_color:
                self.hex_input.setText(hex_color)
    
    def hex_changed(self, hex_text):
        if not hex_text.startswith('#') and hex_text:
            hex_text = '#' + hex_text
            self.hex_input.setText(hex_text)
            return
            
        try:
            if len(hex_text) == 7 and hex_text.startswith('#'):
                color = QColor(hex_text)
                if color.isValid():
                    self.update_preview(color)
                    color_dict = {
                        'r': color.red(),
                        'g': color.green(),
                        'b': color.blue(),
                        'a': 255
                    }
                    self.color_changed.emit(color_dict)
                    
                    if hex_text.upper() not in DEFAULT_COLORS.values():
                        self.preset_combo.setCurrentText("Custom")
                    else:
                        for name, preset_hex in DEFAULT_COLORS.items():
                            if preset_hex.upper() == hex_text.upper():
                                self.preset_combo.setCurrentText(name)
                                break
        except:
            pass
    
    def update_preview(self, color):
        self.color_preview.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #666;"
        )
    
    def set_color(self, color_dict):
        color = QColor(color_dict['r'], color_dict['g'], color_dict['b'])
        hex_color = color.name().upper()
        self.hex_input.setText(hex_color)
        self.update_preview(color)
        
        for name, preset_hex in DEFAULT_COLORS.items():
            if preset_hex.upper() == hex_color:
                self.preset_combo.setCurrentText(name)
                return
        self.preset_combo.setCurrentText("Custom")

class CrosshairMenu(QWidget):
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, config):
        super().__init__()
        self.config = config.copy()
        self.preset_manager = CrosshairPresetManager()
        self.current_preset_name = "Default Green"
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        self.setWindowTitle("Crosshair Settings")
        self.setFixedSize(650, 550)
        # Removed Qt.Tool flag which can cause issues
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        main_layout = QHBoxLayout()
        
        left_layout = QVBoxLayout()
        
        self.preview_widget = CrosshairPreview()
        self.preview_widget.setMinimumSize(200, 400)
        self.preview_widget.setStyleSheet("border: 1px solid gray; background-color: #2b2b2b;")
        
        layout = left_layout
        
        title = QLabel("Crosshair Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Preset management
        preset_group = QGroupBox("Crosshair Presets")
        preset_layout = QVBoxLayout()
        
        # Preset selector
        preset_selector_layout = QHBoxLayout()
        preset_selector_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.update_preset_combo()
        self.preset_combo.currentTextChanged.connect(self.preset_changed)
        preset_selector_layout.addWidget(self.preset_combo)
        preset_layout.addLayout(preset_selector_layout)
        
        # Preset management buttons
        preset_buttons_layout = QHBoxLayout()
        
        self.save_preset_button = QPushButton("Save Current as Preset")
        self.save_preset_button.clicked.connect(self.save_current_as_preset)
        preset_buttons_layout.addWidget(self.save_preset_button)
        
        self.delete_preset_button = QPushButton("Delete Preset")
        self.delete_preset_button.clicked.connect(self.delete_current_preset)
        preset_buttons_layout.addWidget(self.delete_preset_button)
        
        preset_layout.addLayout(preset_buttons_layout)
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # Style selector
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Style:"))
        self.style_combo = QComboBox()
        self.style_combo.addItem("Cross", "cross")
        self.style_combo.addItem("Dot", "dot")
        self.style_combo.currentIndexChanged.connect(self.update_style)
        style_layout.addWidget(self.style_combo)
        style_layout.addStretch()
        layout.addLayout(style_layout)
        
        # Dot size slider (hidden unless dot is selected)
        dot_size_layout = QHBoxLayout()
        dot_size_layout.addWidget(QLabel("Dot Size:"))
        self.dot_size_slider = QSlider(Qt.Horizontal)
        self.dot_size_slider.setRange(2, 50)
        self.dot_size_slider.valueChanged.connect(self.update_dot_size)
        self.dot_size_label = QLabel("6")
        dot_size_layout.addWidget(self.dot_size_slider)
        dot_size_layout.addWidget(self.dot_size_label)
        layout.addLayout(dot_size_layout)
        self.dot_size_layout = dot_size_layout
        
        # Color settings
        color_group = QGroupBox("Colors")
        color_layout = QVBoxLayout()
        
        self.main_color_widget = HexColorWidget(self.config['color'], "Crosshair Color")
        self.main_color_widget.color_changed.connect(self.update_main_color)
        color_layout.addWidget(self.main_color_widget)
        
        self.outline_checkbox = QCheckBox("Enable Outline")
        self.outline_checkbox.toggled.connect(self.update_outline)
        color_layout.addWidget(self.outline_checkbox)
        
        self.outline_color_widget = HexColorWidget(self.config['outline_color'], "Outline Color")
        self.outline_color_widget.color_changed.connect(self.update_outline_color)
        color_layout.addWidget(self.outline_color_widget)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # Size settings
        size_group = QGroupBox("Size & Spacing")
        size_layout = QVBoxLayout()
        
        thickness_layout = QHBoxLayout()
        thickness_layout.addWidget(QLabel("Line Thickness:"))
        self.thickness_spinbox = QSpinBox()
        self.thickness_spinbox.setRange(1, 10)
        self.thickness_spinbox.valueChanged.connect(self.update_thickness)
        thickness_layout.addWidget(self.thickness_spinbox)
        thickness_layout.addStretch()
        size_layout.addLayout(thickness_layout)
        
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Crosshair Length:"))
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setRange(2, 50)
        self.length_slider.valueChanged.connect(self.update_length)
        self.length_label = QLabel("8")
        length_layout.addWidget(self.length_slider)
        length_layout.addWidget(self.length_label)
        size_layout.addLayout(length_layout)
        
        gap_layout = QHBoxLayout()
        gap_layout.addWidget(QLabel("Center Gap:"))
        self.gap_slider = QSlider(Qt.Horizontal)
        self.gap_slider.setRange(0, 20)
        self.gap_slider.valueChanged.connect(self.update_gap)
        self.gap_label = QLabel("2")
        gap_layout.addWidget(self.gap_slider)
        gap_layout.addWidget(self.gap_label)
        size_layout.addLayout(gap_layout)
        
        outline_thickness_layout = QHBoxLayout()
        outline_thickness_layout.addWidget(QLabel("Outline Thickness:"))
        self.outline_thickness_spinbox = QSpinBox()
        self.outline_thickness_spinbox.setRange(1, 5)
        self.outline_thickness_spinbox.valueChanged.connect(self.update_outline_thickness)
        outline_thickness_layout.addWidget(self.outline_thickness_spinbox)
        outline_thickness_layout.addStretch()
        size_layout.addLayout(outline_thickness_layout)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("Reset to Default")
        reset_button.clicked.connect(self.reset_to_default)
        button_layout.addWidget(reset_button)
        
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        instructions = QLabel("Hotkey registered to toggle menu\nPress ESC to close\nRight-click tray icon for options")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(instructions)
        
        layout.addStretch()
        left_layout.addLayout(layout)
        
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.preview_widget)
        
        self.setLayout(main_layout)
    
    def load_settings(self):
        self.main_color_widget.set_color(self.config['color'])
        self.outline_color_widget.set_color(self.config['outline_color'])
        self.thickness_spinbox.setValue(self.config['line_thickness'])
        self.length_slider.setValue(self.config['crosshair_length'])
        self.length_label.setText(str(self.config['crosshair_length']))
        self.gap_slider.setValue(self.config['crosshair_gap'])
        self.gap_label.setText(str(self.config['crosshair_gap']))
        self.outline_checkbox.setChecked(self.config['outline_enabled'])
        self.outline_thickness_spinbox.setValue(self.config['outline_thickness'])
        self.style_combo.setCurrentIndex(0 if self.config.get('crosshair_style', 'cross') == 'cross' else 1)
        self.dot_size_slider.setValue(self.config.get('dot_size', 6))
        self.dot_size_label.setText(str(self.config.get('dot_size', 6)))
        self.update_dot_size_visibility()
        
        # Update preset combo to reflect current settings
        if hasattr(self, 'preset_combo'):
            self.update_preset_combo()
        
        if hasattr(self, 'preview_widget'):
            self.preview_widget.update_config(self.config)
    
    def update_style(self, idx):
        style = self.style_combo.currentData()
        self.config['crosshair_style'] = style
        self.update_dot_size_visibility()
        self.emit_settings()
    
    def update_dot_size_visibility(self):
        is_dot = self.config.get('crosshair_style', 'cross') == 'dot'
        for i in range(self.dot_size_layout.count()):
            widget = self.dot_size_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(is_dot)
    
    def update_dot_size(self, value):
        self.dot_size_label.setText(str(value))
        self.config['dot_size'] = value
        self.emit_settings()
    
    def update_main_color(self, color_dict):
        self.config['color'] = color_dict
        self.emit_settings()
    
    def update_outline_color(self, color_dict):
        self.config['outline_color'] = color_dict
        self.emit_settings()
    
    def update_thickness(self, value):
        self.config['line_thickness'] = value
        self.emit_settings()
    
    def update_length(self, value):
        self.length_label.setText(str(value))
        self.config['crosshair_length'] = value
        self.emit_settings()
    
    def update_gap(self, value):
        self.gap_label.setText(str(value))
        self.config['crosshair_gap'] = value
        self.emit_settings()
    
    def update_outline(self, checked):
        self.config['outline_enabled'] = checked
        self.emit_settings()
    
    def update_outline_thickness(self, value):
        self.config['outline_thickness'] = value
        self.emit_settings()
    
    def emit_settings(self):
        self.settings_changed.emit(self.config)
        if hasattr(self, 'preview_widget'):
            self.preview_widget.update_config(self.config)
        
        # Update preset combo to show "Custom" if current settings don't match any preset
        self.update_preset_combo_for_current_settings()
    
    def update_preset_combo_for_current_settings(self):
        """Update preset combo to show which preset matches current settings, or 'Custom'"""
        preset_names = self.preset_manager.get_preset_names()
        current_preset = None
        
        for name in preset_names:
            preset_config = self.preset_manager.get_preset(name)
            if preset_config == self.config:
                current_preset = name
                break
        
        if current_preset and current_preset != self.current_preset_name:
            self.current_preset_name = current_preset
            self.preset_combo.setCurrentText(current_preset)
        elif not current_preset and self.current_preset_name in preset_names:
            # Settings don't match any preset, show "Custom"
            self.current_preset_name = "Custom"
            if "Custom" not in [self.preset_combo.itemText(i) for i in range(self.preset_combo.count())]:
                self.preset_combo.addItem("Custom")
            self.preset_combo.setCurrentText("Custom")
    
    def reset_to_default(self):
        self.config = self.preset_manager.get_preset("Default Green").copy()
        self.current_preset_name = "Default Green"
        self.load_settings()
        self.emit_settings()
    
    def save_settings(self):
        try:
            with open('crosshair_settings.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def update_preset_combo(self):
        """Update the preset combo box with current presets"""
        self.preset_combo.clear()
        preset_names = self.preset_manager.get_preset_names()
        for name in preset_names:
            self.preset_combo.addItem(name)
        
        # Set current preset
        if self.current_preset_name in preset_names:
            self.preset_combo.setCurrentText(self.current_preset_name)
        elif preset_names:
            self.preset_combo.setCurrentText(preset_names[0])
    
    def preset_changed(self, preset_name):
        """Handle preset selection change"""
        if preset_name and preset_name != self.current_preset_name:
            self.current_preset_name = preset_name
            new_config = self.preset_manager.get_preset(preset_name)
            self.config = new_config.copy()
            self.load_settings()
            self.emit_settings()
    
    def save_current_as_preset(self):
        """Save current configuration as a new preset"""
        name, ok = QInputDialog.getText(self, "Save Preset", 
                                       "Enter preset name:", 
                                       text=f"Custom Preset {len(self.preset_manager.get_preset_names()) + 1}")
        if ok and name:
            if name in self.preset_manager.get_preset_names():
                QMessageBox.warning(self, "Error", "A preset with this name already exists!")
                return
            
            if self.preset_manager.save_current_as_preset(name, self.config):
                self.update_preset_combo()
                self.current_preset_name = name
                self.preset_combo.setCurrentText(name)
                print(f"Preset '{name}' saved successfully")
            else:
                print("Failed to save preset")
    
    def delete_current_preset(self):
        """Delete the currently selected preset"""
        if not self.current_preset_name:
            return
            
        # Don't allow deletion of default presets
        if self.current_preset_name in DEFAULT_PRESETS:
            QMessageBox.warning(self, "Cannot Delete", 
                              f"Cannot delete default preset '{self.current_preset_name}'")
            return
        
        reply = QMessageBox.question(self, "Delete Preset", 
                                   f"Are you sure you want to delete '{self.current_preset_name}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.preset_manager.delete_preset(self.current_preset_name):
                self.update_preset_combo()
                # Switch to first available preset
                preset_names = self.preset_manager.get_preset_names()
                if preset_names:
                    self.current_preset_name = preset_names[0]
                    self.preset_changed(self.current_preset_name)
                print(f"Preset '{self.current_preset_name}' deleted successfully")
            else:
                print("Failed to delete preset")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        super().keyPressEvent(event)

    def closeEvent(self, event):
        QApplication.quit()

class CrosshairOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.menu_visible = False
        self.setup_window()
        self.setup_menu()
        self.setup_system_tray()
        self.setup_global_hotkeys()
        # Fallback timer for testing
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.test_menu_toggle)
    
    def load_config(self):
        try:
            # First try to load from the old settings file
            if os.path.exists('crosshair_settings.json'):
                with open('crosshair_settings.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        # If no settings file exists, use the default preset
        preset_manager = CrosshairPresetManager()
        return preset_manager.get_preset("Default Green")
    
    def setup_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        self.setFocusPolicy(Qt.NoFocus)  # Changed from StrongFocus to NoFocus
        
        self.make_click_through()
    
    def setup_menu(self):
        self.menu = CrosshairMenu(self.config)
        self.menu.settings_changed.connect(self.update_config)
    
    def setup_system_tray(self):
        """Setup system tray icon for easy access"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Create a simple icon (you might want to use a proper icon file)
            icon = QIcon()  # Empty icon for now
            self.tray_icon.setIcon(icon)
            
            # Create tray menu
            tray_menu = QMenu()
            
            show_settings_action = tray_menu.addAction("Show Settings")
            show_settings_action.triggered.connect(self.show_menu)
            
            tray_menu.addSeparator()
            
            exit_action = tray_menu.addAction("Exit")
            exit_action.triggered.connect(QApplication.quit)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            # Double-click to show settings
            self.tray_icon.activated.connect(self.tray_icon_activated)
        else:
            print("System tray not available")
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_menu()
    
    def setup_global_hotkeys(self):
        try:
            self.hotkey_listener = ImprovedHotKeyListener()
            self.hotkey_listener.hotkey_pressed.connect(self.handle_hotkey)
            self.hotkey_listener.start()
        except Exception as e:
            print(f"Failed to setup global hotkeys: {e}")
            print("You can still use the system tray to access settings")
    
    def handle_hotkey(self, action):
        if action == "toggle":
            self.toggle_menu()
    
    def test_menu_toggle(self):
        """Test function to verify menu can be shown"""
        self.show_menu()
        self.test_timer.stop()
    
    def make_click_through(self):
        try:
            hwnd = self.winId().__int__()
            
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_style = style | WS_EX_LAYERED | WS_EX_TRANSPARENT
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            
        except Exception as e:
            print(f"Warning: Could not set click-through mode: {e}")
    
    def disable_click_through(self):
        try:
            hwnd = self.winId().__int__()
            
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_style = (style | WS_EX_LAYERED) & ~WS_EX_TRANSPARENT
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            
        except Exception as e:
            print(f"Warning: Could not disable click-through mode: {e}")
    
    def update_config(self, new_config):
        self.config = new_config
        self.update()
    
    def show_menu(self):
        """Force show the menu"""
        print("Showing settings menu...")
        
        # Center the menu on screen
        screen_geometry = QApplication.primaryScreen().geometry()
        menu_x = (screen_geometry.width() - self.menu.width()) // 2
        menu_y = (screen_geometry.height() - self.menu.height()) // 2
        self.menu.move(menu_x, menu_y)
        
        self.menu.show()
        self.menu.raise_()
        self.menu.activateWindow()
        self.menu_visible = True
        
        # Don't disable click-through for the overlay - menu is separate window
        
    def hide_menu(self):
        """Hide the menu"""
        self.menu.hide()
        self.menu_visible = False
        # Ensure click-through is restored
        self.make_click_through()

    
    def toggle_menu(self):
        if self.menu.isVisible():
            self.hide_menu()
        else:
            self.show_menu()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        w = self.width()
        h = self.height()
        center_x = w // 2
        center_y = h // 2
        
        main_color = QColor(self.config['color']['r'], self.config['color']['g'], 
                           self.config['color']['b'], self.config['color']['a'])
        outline_color = QColor(self.config['outline_color']['r'], self.config['outline_color']['g'], 
                              self.config['outline_color']['b'], self.config['outline_color']['a'])
        
        thickness = self.config['line_thickness']
        length = self.config['crosshair_length']
        gap = self.config['crosshair_gap']
        outline_enabled = self.config['outline_enabled']
        outline_thickness = self.config['outline_thickness']
        crosshair_style = self.config.get('crosshair_style', 'cross')
        dot_size = self.config.get('dot_size', 6)
        
        if crosshair_style == 'dot':
            # Draw outline first if enabled
            if outline_enabled:
                painter.setPen(Qt.NoPen)
                painter.setBrush(outline_color)
                painter.drawEllipse(center_x - dot_size//2 - outline_thickness, center_y - dot_size//2 - outline_thickness, dot_size + 2*outline_thickness, dot_size + 2*outline_thickness)
            # Draw main dot
            painter.setPen(Qt.NoPen)
            painter.setBrush(main_color)
            painter.drawEllipse(center_x - dot_size//2, center_y - dot_size//2, dot_size, dot_size)
        else:
            if outline_enabled:
                outline_pen = QPen(outline_color, thickness + outline_thickness * 2)
                outline_pen.setCosmetic(True)
                outline_pen.setCapStyle(Qt.FlatCap)
                outline_pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(outline_pen)
                painter.drawLine(QLineF(center_x + 0.5, center_y - length - gap + 0.5, center_x + 0.5, center_y - gap + 0.5))
                painter.drawLine(QLineF(center_x + 0.5, center_y + gap + 0.5, center_x + 0.5, center_y + length + gap + 0.5))
                painter.drawLine(QLineF(center_x - length - gap + 0.5, center_y + 0.5, center_x - gap + 0.5, center_y + 0.5))
                painter.drawLine(QLineF(center_x + gap + 0.5, center_y + 0.5, center_x + length + gap + 0.5, center_y + 0.5))
            main_pen = QPen(main_color, thickness)
            main_pen.setCosmetic(True)
            main_pen.setCapStyle(Qt.FlatCap)
            main_pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(main_pen)
            painter.drawLine(QLineF(center_x + 0.5, center_y - length - gap + 0.5, center_x + 0.5, center_y - gap + 0.5))
            painter.drawLine(QLineF(center_x + 0.5, center_y + gap + 0.5, center_x + 0.5, center_y + length + gap + 0.5))
            painter.drawLine(QLineF(center_x - length - gap + 0.5, center_y + 0.5, center_x - gap + 0.5, center_y + 0.5))
            painter.drawLine(QLineF(center_x + gap + 0.5, center_y + 0.5, center_x + length + gap + 0.5, center_y + 0.5))
        painter.end()
    
    def keyPressEvent(self, event):
        # Manual hotkeys as fallback
        if event.key() == Qt.Key_F2:
            self.toggle_menu()
        elif event.key() == Qt.Key_Escape:
            if self.menu_visible:
                self.hide_menu()
            else:
                QApplication.quit()
        # Test hotkey
        elif event.key() == Qt.Key_F12:
            print("F12 pressed - testing menu visibility")
            self.test_timer.start(100)  # Show menu after 100ms
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        if hasattr(self, 'hotkey_listener'):
            self.hotkey_listener.stop()
        event.accept()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    try:
        script = sys.argv[0]
        params = " ".join(sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
    except Exception as e:
        print(f"Error requesting admin privileges: {e}")
        return False
    return True

def main():
    # Single instance enforcement
    shared_memory = QSharedMemory("CrosshairOverlayUniqueKey")
    if not shared_memory.create(1):
        print("Another instance is already running.")
        sys.exit(0)
    # Try to get admin privileges but don't exit if it fails
    #if not is_admin():
    #    print("Requesting administrator privileges for better global hotkey support...")
    #    print("If this fails, you can still use the system tray icon to access settings.")
    #    try:
    #        if run_as_admin():
    #            sys.exit(0)
    #    except:
    #        print("Failed to get admin privileges. Continuing without admin rights.")
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when overlay is hidden
    
    # Check if system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("System Tray is not available on this system.")
        app.setQuitOnLastWindowClosed(True)
    
    overlay = CrosshairOverlay()
    overlay.show()
    
    # Handle Ctrl+C gracefully
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    print("=" * 50)
    print("Crosshair overlay started successfully!")
    print("=" * 50)
    print("Controls:")
    print("- Global hotkey (F2/F3/etc.) to toggle settings")
    print("- F12 to test menu visibility")
    print("- Right-click system tray icon for options")
    print("- ESC to close settings or exit")
    print("=" * 50)
    print("If global hotkeys don't work, use the system tray icon!")
    
    # Test the menu after a short delay
    QTimer.singleShot(2000, overlay.test_menu_toggle)
    
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()