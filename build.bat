@echo off
echo Building Crosshair Overlay...

REM Check if Rust is installed
where cargo >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Rust is not installed. Please install Rust from https://rustup.rs/
    pause
    exit /b 1
)

REM Build in release mode for optimal performance
echo Compiling in release mode...
cargo build --release

if %errorlevel% equ 0 (
    echo Build successful!
    echo Running Crosshair Overlay...
    echo Controls:
    echo   S - Toggle settings
    echo   H - Toggle overlay
    echo   ESC - Exit
    echo.
    target\release\crosshair_overlay.exe
) else (
    echo Build failed!
    pause
    exit /b 1
) 