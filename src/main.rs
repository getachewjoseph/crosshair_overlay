use eframe::{egui, NativeOptions};

mod crosshair;
mod settings;

use crosshair::CrosshairOverlay;

fn main() -> Result<(), eframe::Error> {
    env_logger::init();
    let options = NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([400.0, 600.0])
            .with_resizable(false)
            .with_transparent(true)
            .with_decorations(false)
            .with_always_on_top(),
        ..Default::default()
    };
    eframe::run_native(
        "Crosshair Overlay",
        options,
        Box::new(|_cc| Box::new(CrosshairOverlay::new())),
    )
} 