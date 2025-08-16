# Crosshair Overlay

A high-performance, minimal crosshair overlay application with support for multiple crosshair presets. Available in both Rust and Python versions.

## Features

- **High Performance**: Built in Rust with egui for optimal rendering performance
- **Minimal Design**: Clean, lightweight overlay that doesn't interfere with your games
- **Multiple Crosshair Presets**: Save and switch between multiple custom crosshair configurations
- **Customizable Crosshairs**: Choose between cross-style or dot crosshairs
- **Real-time Settings**: Adjust colors, sizes, and styles with live preview
- **Color Presets**: Quick access to popular colors (Green, Red, Blue, White, etc.)
- **Outline Support**: Optional outline for better visibility
- **Keyboard Shortcuts**: Quick access to settings and controls
- **Settings Persistence**: Your preferences are automatically saved
- **Preset Management**: Save, load, and manage multiple crosshair configurations

## Crosshair Types

### Cross Crosshair
- Adjustable line thickness
- Configurable crosshair length
- Customizable gap size
- Optional outline

### Dot Crosshair
- Adjustable dot size
- Optional outline
- Perfect for precision aiming

## Multiple Crosshair Presets

The application now supports saving and managing multiple crosshair configurations:

### Default Presets
- **Default Green**: Classic green crosshair with black outline
- **Red Dot**: Red dot crosshair for precision aiming
- **Blue Cross**: Blue crosshair with white outline
- **White Minimal**: Clean white crosshair without outline

### Custom Presets
- Save your own custom crosshair configurations
- Switch between presets instantly
- Delete custom presets (default presets are protected)
- All presets are automatically saved to `crosshair_presets.json`

### Preset Management
- **Save Current as Preset**: Save your current settings as a new preset
- **Delete Preset**: Remove custom presets (default presets cannot be deleted)
- **Preset Dropdown**: Quick switching between saved presets
- **Live Preview**: See changes immediately when switching presets

## Controls

### Rust Version
- **S**: Toggle settings panel
- **H**: Toggle overlay visibility
- **ESC**: Exit application

### Python Version
- **Global Hotkey** (F2/F3/etc.): Toggle settings menu
- **F12**: Test menu visibility
- **ESC**: Close settings or exit
- **System Tray**: Right-click for options

## Installation

### Rust Version

#### Prerequisites
- Rust (latest stable version)
- Cargo

#### Build and Run

1. Clone the repository:
```bash
git clone <repository-url>
cd crosshair_overlay
```

2. Build the project:
```bash
cargo build --release
```

3. Run the application:
```bash
cargo run --release
```

### Python Version

#### Prerequisites
- Python 3.6+
- PyQt5

#### Install Dependencies
```bash
pip install PyQt5
```

#### Run the Application
```bash
python crosshair_script.py
```

## Configuration

### Rust Version
The application automatically saves your settings to `crosshair_settings.json` in the same directory.

### Python Version
The application saves:
- **Settings**: `crosshair_settings.json` (legacy format)
- **Presets**: `crosshair_presets.json` (multiple crosshair configurations)

You can:
- Adjust colors using RGB sliders or preset options
- Modify crosshair dimensions
- Enable/disable outlines
- Switch between cross and dot crosshairs
- Save multiple custom crosshair configurations
- Switch between saved presets instantly

## Performance

This Rust implementation provides:
- **Minimal CPU usage**: Efficient rendering with egui
- **Low memory footprint**: Optimized for gaming scenarios
- **Smooth overlay**: Hardware-accelerated graphics
- **No input lag**: Non-blocking overlay rendering

## Technical Details

### Rust Version
- **Language**: Rust
- **GUI Framework**: egui
- **Window Management**: winit
- **Graphics**: OpenGL via glow
- **Serialization**: serde_json
- **Platform**: Cross-platform (Windows, macOS, Linux)

### Python Version
- **Language**: Python 3
- **GUI Framework**: PyQt5
- **Window Management**: Qt
- **Graphics**: Qt Graphics
- **Serialization**: JSON
- **Platform**: Cross-platform (Windows, macOS, Linux)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.