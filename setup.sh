#!/bin/bash

echo "Crosshair Overlay Setup"
echo "======================"

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "Rust is not installed. Installing Rust..."
    echo "Please visit https://rustup.rs/ to install Rust, or run:"
    echo "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo ""
    echo "After installing Rust, run this script again."
    exit 1
fi

echo "Rust is installed. Checking version..."
rustc --version
cargo --version

echo ""
echo "Installing dependencies..."
cargo build

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup complete! You can now run the application with:"
    echo "  cargo run --release"
    echo "  or"
    echo "  ./build.sh"
else
    echo "Setup failed! Please check the error messages above."
    exit 1
fi 