use crate::settings::{Settings, Color, CrosshairType};
use eframe::egui::{self, Pos2, Rect, Stroke, Vec2, Ui, Slider, ComboBox};
use std::collections::HashMap;

pub struct CrosshairOverlay {
    settings: Settings,
    show_settings: bool,
    overlay_visible: bool,
    color_presets: HashMap<String, Color>,
}

impl CrosshairOverlay {
    pub fn new() -> Self {
        let mut color_presets = HashMap::new();
        color_presets.insert("Green".to_string(), Color::new(0, 255, 0, 255));
        color_presets.insert("Red".to_string(), Color::new(255, 0, 0, 255));
        color_presets.insert("Blue".to_string(), Color::new(0, 0, 255, 255));
        color_presets.insert("White".to_string(), Color::new(255, 255, 255, 255));
        color_presets.insert("Yellow".to_string(), Color::new(255, 255, 0, 255));
        color_presets.insert("Cyan".to_string(), Color::new(0, 255, 255, 255));
        color_presets.insert("Magenta".to_string(), Color::new(255, 0, 255, 255));
        color_presets.insert("Orange".to_string(), Color::new(255, 165, 0, 255));
        color_presets.insert("Pink".to_string(), Color::new(255, 105, 180, 255));
        color_presets.insert("Purple".to_string(), Color::new(128, 0, 128, 255));

        Self {
            settings: Settings::load(),
            show_settings: false,
            overlay_visible: true,
            color_presets,
        }
    }

    fn draw_crosshair(&self, painter: &egui::Painter, center: Pos2) {
        match self.settings.crosshair_type {
            CrosshairType::Cross => self.draw_cross_crosshair(painter, center),
            CrosshairType::Dot => self.draw_dot_crosshair(painter, center),
        }
    }

    fn draw_cross_crosshair(&self, painter: &egui::Painter, center: Pos2) {
        let length = self.settings.crosshair_length;
        let gap = self.settings.crosshair_gap;
        let thickness = self.settings.line_thickness;

        // Draw outline if enabled
        if self.settings.outline_enabled {
            let outline_thickness = thickness + self.settings.outline_thickness * 2.0;
            let outline_stroke = Stroke::new(outline_thickness, self.settings.outline_color.to_color32());
            
            // Vertical lines
            painter.line_segment(
                [Pos2::new(center.x, center.y - length - gap), Pos2::new(center.x, center.y - gap)],
                outline_stroke,
            );
            painter.line_segment(
                [Pos2::new(center.x, center.y + gap), Pos2::new(center.x, center.y + length + gap)],
                outline_stroke,
            );
            
            // Horizontal lines
            painter.line_segment(
                [Pos2::new(center.x - length - gap, center.y), Pos2::new(center.x - gap, center.y)],
                outline_stroke,
            );
            painter.line_segment(
                [Pos2::new(center.x + gap, center.y), Pos2::new(center.x + length + gap, center.y)],
                outline_stroke,
            );
        }

        // Draw main crosshair
        let main_stroke = Stroke::new(thickness, self.settings.color.to_color32());
        
        // Vertical lines
        painter.line_segment(
            [Pos2::new(center.x, center.y - length - gap), Pos2::new(center.x, center.y - gap)],
            main_stroke,
        );
        painter.line_segment(
            [Pos2::new(center.x, center.y + gap), Pos2::new(center.x, center.y + length + gap)],
            main_stroke,
        );
        
        // Horizontal lines
        painter.line_segment(
            [Pos2::new(center.x - length - gap, center.y), Pos2::new(center.x - gap, center.y)],
            main_stroke,
        );
        painter.line_segment(
            [Pos2::new(center.x + gap, center.y), Pos2::new(center.x + length + gap, center.y)],
            main_stroke,
        );
    }

    fn draw_dot_crosshair(&self, painter: &egui::Painter, center: Pos2) {
        let dot_size = self.settings.dot_size;
        
        // Draw outline if enabled
        if self.settings.outline_enabled {
            let outline_size = dot_size + self.settings.outline_thickness * 2.0;
            painter.circle_filled(center, outline_size, self.settings.outline_color.to_color32());
        }
        
        // Draw main dot
        painter.circle_filled(center, dot_size, self.settings.color.to_color32());
    }

    fn render_settings_panel(&mut self, ui: &mut Ui) {
        ui.heading("Crosshair Settings");
        ui.separator();

        // Crosshair Type
        ui.label("Crosshair Type:");
        ComboBox::from_id_source("crosshair_type")
            .selected_text(match self.settings.crosshair_type {
                CrosshairType::Cross => "Cross",
                CrosshairType::Dot => "Dot",
            })
            .show_ui(ui, |ui| {
                ui.selectable_value(&mut self.settings.crosshair_type, CrosshairType::Cross, "Cross");
                ui.selectable_value(&mut self.settings.crosshair_type, CrosshairType::Dot, "Dot");
            });

        ui.separator();

        // Color Settings
        ui.heading("Color Settings");
        
        // Main Color
        ui.label("Main Color:");
        render_color_picker(ui, &mut self.settings.color, "main_color", &self.color_presets);
        
        // Outline Color
        ui.label("Outline Color:");
        render_color_picker(ui, &mut self.settings.outline_color, "outline_color", &self.color_presets);
        
        ui.checkbox(&mut self.settings.outline_enabled, "Enable Outline");

        ui.separator();

        // Size Settings
        ui.heading("Size Settings");
        
        match self.settings.crosshair_type {
            CrosshairType::Cross => {
                ui.label("Line Thickness:");
                ui.add(Slider::new(&mut self.settings.line_thickness, 1.0..=10.0));
                
                ui.label("Crosshair Length:");
                ui.add(Slider::new(&mut self.settings.crosshair_length, 1.0..=20.0));
                
                ui.label("Crosshair Gap:");
                ui.add(Slider::new(&mut self.settings.crosshair_gap, 0.0..=10.0));
                
                if self.settings.outline_enabled {
                    ui.label("Outline Thickness:");
                    ui.add(Slider::new(&mut self.settings.outline_thickness, 0.5..=5.0));
                }
            }
            CrosshairType::Dot => {
                ui.label("Dot Size:");
                ui.add(Slider::new(&mut self.settings.dot_size, 1.0..=15.0));
                
                if self.settings.outline_enabled {
                    ui.label("Outline Thickness:");
                    ui.add(Slider::new(&mut self.settings.outline_thickness, 0.5..=5.0));
                }
            }
        }

        ui.separator();

        // Controls
        ui.horizontal(|ui| {
            if ui.button("Reset to Default").clicked() {
                self.settings = Settings::default();
            }
            
            if ui.button("Save Settings").clicked() {
                if let Err(e) = self.settings.save() {
                    eprintln!("Failed to save settings: {}", e);
                }
            }
        });

        ui.separator();
        
        ui.label("Press 'S' to toggle settings");
        ui.label("Press 'H' to toggle overlay");
        ui.label("Press 'ESC' to exit");
    }
}

fn render_color_picker(ui: &mut Ui, color: &mut Color, id: &str, color_presets: &HashMap<String, Color>) {
    ui.horizontal(|ui| {
        // Color preset dropdown
        ComboBox::from_id_source(format!("{}_preset", id))
            .selected_text("Custom")
            .show_ui(ui, |ui| {
                ui.selectable_value(&mut (), (), "Custom");
                for (name, preset_color) in color_presets {
                    if ui.selectable_label(false, name).clicked() {
                        *color = preset_color.clone();
                    }
                }
            });

        // Color preview
        let rect = Rect::from_min_size(
            ui.cursor().min,
            Vec2::new(30.0, 20.0),
        );
        ui.painter().rect_filled(rect, 0.0, color.to_color32());
        ui.allocate_ui(Vec2::new(30.0, 20.0), |_| {});
    });

    // RGB sliders
    ui.horizontal(|ui| {
        ui.label("R:");
        ui.add(Slider::new(&mut color.r, 0..=255).text(""));
    });
    ui.horizontal(|ui| {
        ui.label("G:");
        ui.add(Slider::new(&mut color.g, 0..=255).text(""));
    });
    ui.horizontal(|ui| {
        ui.label("B:");
        ui.add(Slider::new(&mut color.b, 0..=255).text(""));
    });
    ui.horizontal(|ui| {
        ui.label("A:");
        ui.add(Slider::new(&mut color.a, 0..=255).text(""));
    });
}

impl eframe::App for CrosshairOverlay {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Handle keyboard shortcuts
        if ctx.input(|i| i.key_pressed(egui::Key::S)) {
            self.show_settings = !self.show_settings;
        }
        
        if ctx.input(|i| i.key_pressed(egui::Key::H)) {
            self.overlay_visible = !self.overlay_visible;
        }
        
        if ctx.input(|i| i.key_pressed(egui::Key::Escape)) {
            std::process::exit(0);
        }

        // Draw the overlay
        if self.overlay_visible {
            let screen_rect = ctx.screen_rect();
            let center = screen_rect.center();
            
            let painter = ctx.layer_painter(egui::LayerId::new(
                egui::Order::Foreground,
                egui::Id::new("crosshair_overlay"),
            ));
            
            self.draw_crosshair(&painter, center);
        }

        // Show settings window
        if self.show_settings {
            egui::Window::new("Crosshair Settings")
                .resizable(false)
                .collapsible(false)
                .show(ctx, |ui| {
                    self.render_settings_panel(ui);
                });
        }
    }
} 