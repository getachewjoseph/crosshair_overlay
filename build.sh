#!/bin/bash

echo "Building Crosshair Overlay..."

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "Error: Rust is not installed. Please install Rust from https://rustup.rs/"
    exit 1
fi

# Build in release mode for optimal performance
echo "Compiling in release mode..."
cargo build --release

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Running Crosshair Overlay..."
    echo "Controls:"
    echo "  S - Toggle settings"
    echo "  H - Toggle overlay"
    echo "  ESC - Exit"
    echo ""
    ./target/release/crosshair_overlay
else
    echo "Build failed!"
    exit 1
fi 