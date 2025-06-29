# Crosshair Overlay

A high-performance, minimal crosshair overlay application written in Rust for maximum performance and efficiency.

## Features

- **High Performance**: Built in Rust with egui for optimal rendering performance
- **Minimal Design**: Clean, lightweight overlay that doesn't interfere with your games
- **Customizable Crosshairs**: Choose between cross-style or dot crosshairs
- **Real-time Settings**: Adjust colors, sizes, and styles with live preview
- **Color Presets**: Quick access to popular colors (Green, Red, Blue, White, etc.)
- **Outline Support**: Optional outline for better visibility
- **Keyboard Shortcuts**: Quick access to settings and controls
- **Settings Persistence**: Your preferences are automatically saved

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

## Controls

- **S**: Toggle settings panel
- **H**: Toggle overlay visibility
- **ESC**: Exit application

## Installation

### Prerequisites
- Rust (latest stable version)
- Cargo

### Build and Run

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

## Configuration

The application automatically saves your settings to `crosshair_settings.json` in the same directory. You can:

- Adjust colors using RGB sliders or preset options
- Modify crosshair dimensions
- Enable/disable outlines
- Switch between cross and dot crosshairs

## Performance

This Rust implementation provides:
- **Minimal CPU usage**: Efficient rendering with egui
- **Low memory footprint**: Optimized for gaming scenarios
- **Smooth overlay**: Hardware-accelerated graphics
- **No input lag**: Non-blocking overlay rendering

## Technical Details

- **Language**: Rust
- **GUI Framework**: egui
- **Window Management**: winit
- **Graphics**: OpenGL via glow
- **Serialization**: serde_json
- **Platform**: Cross-platform (Windows, macOS, Linux)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.