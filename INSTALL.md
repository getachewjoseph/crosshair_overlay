# Installation Guide

## Prerequisites

### Installing Rust

1. **Visit https://rustup.rs/** or run the following command:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Follow the installation prompts** (usually just press 1 for default installation)

3. **Restart your terminal** or run:
   ```bash
   source ~/.cargo/env
   ```

4. **Verify installation**:
   ```bash
   rustc --version
   cargo --version
   ```

## Building and Running

### Option 1: Using the build script (Recommended)

**On macOS/Linux:**
```bash
./build.sh
```

**On Windows:**
```cmd
build.bat
```

### Option 2: Manual build

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd crosshair_overlay
   ```

2. **Build the project:**
   ```bash
   cargo build --release
   ```

3. **Run the application:**
   ```bash
   cargo run --release
   ```

## Usage

### Controls
- **S**: Toggle settings panel
- **H**: Toggle overlay visibility  
- **ESC**: Exit application

### Features
- **Crosshair Types**: Switch between cross and dot crosshairs
- **Color Customization**: Use RGB sliders or preset colors
- **Size Adjustment**: Modify thickness, length, gap, and dot size
- **Outline Support**: Enable/disable outlines for better visibility
- **Settings Persistence**: Your preferences are automatically saved

## Troubleshooting

### Common Issues

1. **"command not found: cargo"**
   - Rust is not installed or not in your PATH
   - Follow the Rust installation steps above

2. **Build errors**
   - Make sure you have the latest Rust version: `rustup update`
   - Check that all dependencies are available

3. **Permission denied on build scripts**
   - Make scripts executable: `chmod +x build.sh setup.sh`

4. **Overlay not visible**
   - Press 'H' to toggle visibility
   - Check that the window is set to "always on top"

### Performance Tips

- Always build with `--release` flag for optimal performance
- Close unnecessary applications to free up system resources
- The overlay is designed to be lightweight and shouldn't impact game performance

## Support

If you encounter any issues, please:
1. Check this installation guide
2. Review the README.md file
3. Open an issue on the project repository 