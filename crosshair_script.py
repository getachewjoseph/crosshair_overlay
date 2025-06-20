import sys
import ctypes
import json
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QSlider, QPushButton, QCheckBox,
                           QGroupBox, QSpinBox, QLineEdit, QComboBox, QSystemTrayIcon, QMenu)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
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
    'outline_thickness': 1
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
        
        # Draw outline first if enabled
        if outline_enabled:
            outline_pen = QPen(outline_color, thickness + outline_thickness * 2)
            painter.setPen(outline_pen)
            
            painter.drawLine(center_x, center_y - length - gap, center_x, center_y - gap)
            painter.drawLine(center_x, center_y + gap, center_x, center_y + length + gap)
            painter.drawLine(center_x - length - gap, center_y, center_x - gap, center_y)
            painter.drawLine(center_x + gap, center_y, center_x + length + gap, center_y)
        
        # Draw main crosshair
        main_pen = QPen(main_color, thickness)
        painter.setPen(main_pen)
        
        painter.drawLine(center_x, center_y - length - gap, center_x, center_y - gap)
        painter.drawLine(center_x, center_y + gap, center_x, center_y + length + gap)
        painter.drawLine(center_x - length - gap, center_y, center_x - gap, center_y)
        painter.drawLine(center_x + gap, center_y, center_x + length + gap, center_y)
        
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
        
        if hasattr(self, 'preview_widget'):
            self.preview_widget.update_config(self.config)
    
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
    
    def reset_to_default(self):
        self.config = DEFAULT_CONFIG.copy()
        self.load_settings()
        self.emit_settings()
    
    def save_settings(self):
        try:
            with open('crosshair_settings.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        super().keyPressEvent(event)

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
            if os.path.exists('crosshair_settings.json'):
                with open('crosshair_settings.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return DEFAULT_CONFIG.copy()
    
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
        
        if outline_enabled:
            outline_pen = QPen(outline_color, thickness + outline_thickness * 2)
            painter.setPen(outline_pen)
            
            painter.drawLine(center_x, center_y - length - gap, center_x, center_y - gap)
            painter.drawLine(center_x, center_y + gap, center_x, center_y + length + gap)
            painter.drawLine(center_x - length - gap, center_y, center_x - gap, center_y)
            painter.drawLine(center_x + gap, center_y, center_x + length + gap, center_y)
        
        main_pen = QPen(main_color, thickness)
        painter.setPen(main_pen)
        
        painter.drawLine(center_x, center_y - length - gap, center_x, center_y - gap)
        painter.drawLine(center_x, center_y + gap, center_x, center_y + length + gap)
        painter.drawLine(center_x - length - gap, center_y, center_x - gap, center_y)
        painter.drawLine(center_x + gap, center_y, center_x + length + gap, center_y)
        
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
