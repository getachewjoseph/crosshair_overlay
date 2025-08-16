use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Color {
    pub r: u8,
    pub g: u8,
    pub b: u8,
    pub a: u8,
}

impl Color {
    pub fn new(r: u8, g: u8, b: u8, a: u8) -> Self {
        Self { r, g, b, a }
    }
    
    pub fn to_color32(&self) -> egui::Color32 {
        egui::Color32::from_rgba_premultiplied(self.r, self.g, self.b, self.a)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Settings {
    pub color: Color,
    pub outline_color: Color,
    pub line_thickness: f32,
    pub crosshair_length: f32,
    pub crosshair_gap: f32,
    pub outline_enabled: bool,
    pub outline_thickness: f32,
    pub crosshair_type: CrosshairType,
    pub dot_size: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum CrosshairType {
    Cross,
    Dot,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            color: Color::new(255, 255, 255, 255), // White
            outline_color: Color::new(0, 0, 0, 255), // Black
            line_thickness: 2.0,
            crosshair_length: 8.0,
            crosshair_gap: 2.0,
            outline_enabled: false,
            outline_thickness: 1.0,
            crosshair_type: CrosshairType::Cross,
            dot_size: 4.0,
        }
    }
}

impl Settings {
    pub fn load() -> Self {
        let settings_path = "crosshair_settings.json";
        if Path::new(settings_path).exists() {
            if let Ok(contents) = fs::read_to_string(settings_path) {
                if let Ok(settings) = serde_json::from_str(&contents) {
                    return settings;
                }
            }
        }
        Settings::default()
    }
    
    pub fn save(&self) -> Result<(), Box<dyn std::error::Error>> {
        let settings_path = "crosshair_settings.json";
        let json = serde_json::to_string_pretty(self)?;
        fs::write(settings_path, json)?;
        Ok(())
    }
} 