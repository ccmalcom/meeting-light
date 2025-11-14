"""
Native macOS settings window for Meeting Light.

Provides a user-friendly interface for configuring:
- API credentials (Govee, Google Calendar)
- Timing thresholds (when colors change)
- Light colors (RGB values)
- Brightness levels
"""

import os
import json
from typing import Optional, Dict, Any
from objc import YES, NO
from AppKit import (
    NSWindow, NSPanel, NSApplication, NSApp,
    NSTextField, NSButton, NSBox, NSColor, NSColorWell,
    NSSlider, NSTextFieldCell,
    NSMakeRect, NSMakePoint, NSMakeSize,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSBackingStoreBuffered,
    NSBezelBorder, NSLineBorder
)
from Foundation import NSObject
from dotenv import set_key, dotenv_values

from config import (
    ENV_FILE_PATH,
    APP_SUPPORT_PATH,
    MEETING_IDLE_THRESHOLD,
    MEETING_SOON_THRESHOLD,
    COLOR_SOON,
    COLOR_IMMINENT,
    COLOR_IN_MEETING,
    TEMPERATURE_IDLE,
    BRIGHTNESS_IDLE,
    BRIGHTNESS_SOON,
    BRIGHTNESS_IMMINENT,
    BRIGHTNESS_IN_MEETING,
)

# User config file path
USER_CONFIG_PATH = os.path.join(APP_SUPPORT_PATH, "user_config.json")


class SettingsDelegate(NSObject):
    """Delegate to handle settings window events."""
    
    def windowWillClose_(self, notification):
        """Called when the window is about to close."""
        NSApp.stopModal()


class SettingsWindow:
    """
    Native macOS settings window for Meeting Light.
    
    Provides a comprehensive interface for all app settings.
    """
    
    def __init__(self):
        """Initialize the settings window."""
        self.window: Optional[NSPanel] = None
        self.fields: Dict[str, Any] = {}
        
        # Load current settings
        self.env_values = dotenv_values(ENV_FILE_PATH)
        self.user_config = self._load_user_config()
    
    def _load_user_config(self) -> Dict[str, Any]:
        """Load user configuration from JSON file."""
        if os.path.exists(USER_CONFIG_PATH):
            try:
                with open(USER_CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_user_config(self) -> None:
        """Save user configuration to JSON file."""
        try:
            with open(USER_CONFIG_PATH, 'w') as f:
                json.dump(self.user_config, f, indent=2)
        except Exception as e:
            print(f"Error saving user config: {e}")
    
    def show(self) -> None:
        """Display the settings window."""
        # Create window
        self.window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 600, 700),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
            NSBackingStoreBuffered,
            NO
        )
        
        self.window.setTitle_("Meeting Light Settings")
        self.window.center()
        
        # Set delegate
        delegate = SettingsDelegate.alloc().init()
        self.window.setDelegate_(delegate)
        
        # Build UI
        y_position = 650
        
        # API Credentials Section
        y_position = self._add_section_header("API Credentials", y_position)
        y_position = self._add_text_field("GOVEE_API_KEY", "Govee API Key:", y_position, secure=True)
        y_position = self._add_text_field("GOVEE_DEVICE_MAC", "Device MAC (XX:XX:XX:XX:XX:XX):", y_position)
        y_position = self._add_text_field("GOVEE_MODEL", "Device Model (e.g., H6159):", y_position)
        y_position = self._add_text_field("GOOGLE_CALENDAR_ID", "Google Calendar ID:", y_position)
        
        y_position -= 20  # Extra spacing
        
        # Timing Section
        y_position = self._add_section_header("Timing (seconds)", y_position)
        y_position = self._add_number_field(
            "meeting_idle_threshold",
            "Meeting Far Away Threshold:",
            y_position,
            default=MEETING_IDLE_THRESHOLD,
            description="(Blue light appears when meeting is within this time)"
        )
        y_position = self._add_number_field(
            "meeting_soon_threshold",
            "Meeting Imminent Threshold:",
            y_position,
            default=MEETING_SOON_THRESHOLD,
            description="(Red light appears when meeting is within this time)"
        )
        
        y_position -= 20  # Extra spacing
        
        # Colors Section
        y_position = self._add_section_header("Light Colors (RGB)", y_position)
        y_position = self._add_color_field("color_idle_temp", "Idle (Warm White):", y_position, 
                                          default=TEMPERATURE_IDLE, is_temperature=True)
        y_position = self._add_color_field("color_soon", "Meeting Soon (Blue):", y_position, 
                                          default=COLOR_SOON)
        y_position = self._add_color_field("color_imminent", "Meeting Imminent (Red):", y_position, 
                                          default=COLOR_IMMINENT)
        y_position = self._add_color_field("color_in_meeting", "In Meeting (White):", y_position, 
                                          default=COLOR_IN_MEETING)
        
        y_position -= 20  # Extra spacing
        
        # Brightness Section
        y_position = self._add_section_header("Brightness (0-100)", y_position)
        y_position = self._add_slider_field("brightness_idle", "Idle:", y_position, 
                                           default=BRIGHTNESS_IDLE)
        y_position = self._add_slider_field("brightness_soon", "Meeting Soon:", y_position, 
                                           default=BRIGHTNESS_SOON)
        y_position = self._add_slider_field("brightness_imminent", "Meeting Imminent:", y_position, 
                                           default=BRIGHTNESS_IMMINENT)
        y_position = self._add_slider_field("brightness_in_meeting", "In Meeting:", y_position, 
                                           default=BRIGHTNESS_IN_MEETING)
        
        # Buttons
        self._add_buttons()
        
        # Show window modally
        NSApp.runModalForWindow_(self.window)
    
    def _add_section_header(self, title: str, y: int) -> int:
        """Add a section header."""
        label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, y, 560, 24))
        label.setStringValue_(title)
        label.setBezeled_(NO)
        label.setDrawsBackground_(NO)
        label.setEditable_(NO)
        label.setSelectable_(NO)
        label.setFont_(label.font().boldFontOfSize_(14))
        self.window.contentView().addSubview_(label)
        
        # Add separator line
        box = NSBox.alloc().initWithFrame_(NSMakeRect(20, y - 5, 560, 1))
        box.setBoxType_(NSLineBorder)
        self.window.contentView().addSubview_(box)
        
        return y - 30
    
    def _add_text_field(self, key: str, label: str, y: int, secure: bool = False) -> int:
        """Add a text field with label."""
        # Label
        label_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, y, 200, 20))
        label_field.setStringValue_(label)
        label_field.setBezeled_(NO)
        label_field.setDrawsBackground_(NO)
        label_field.setEditable_(NO)
        label_field.setSelectable_(NO)
        self.window.contentView().addSubview_(label_field)
        
        # Text field
        text_field = NSTextField.alloc().initWithFrame_(NSMakeRect(230, y, 350, 24))
        current_value = self.env_values.get(key, "")
        text_field.setStringValue_(current_value)
        
        if secure:
            text_field.setPlaceholderString_("Enter your API key")
        
        self.window.contentView().addSubview_(text_field)
        self.fields[key] = text_field
        
        return y - 35
    
    def _add_number_field(self, key: str, label: str, y: int, default: int, description: str = "") -> int:
        """Add a number field with label."""
        # Label
        label_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, y, 200, 20))
        label_field.setStringValue_(label)
        label_field.setBezeled_(NO)
        label_field.setDrawsBackground_(NO)
        label_field.setEditable_(NO)
        label_field.setSelectable_(NO)
        self.window.contentView().addSubview_(label_field)
        
        # Number field
        number_field = NSTextField.alloc().initWithFrame_(NSMakeRect(230, y, 80, 24))
        current_value = self.user_config.get(key, default)
        number_field.setStringValue_(str(current_value))
        self.window.contentView().addSubview_(number_field)
        self.fields[key] = number_field
        
        # Description
        if description:
            desc_field = NSTextField.alloc().initWithFrame_(NSMakeRect(320, y, 260, 20))
            desc_field.setStringValue_(description)
            desc_field.setBezeled_(NO)
            desc_field.setDrawsBackground_(NO)
            desc_field.setEditable_(NO)
            desc_field.setSelectable_(NO)
            desc_field.setTextColor_(NSColor.grayColor())
            desc_field.setFont_(desc_field.font().fontWithSize_(11))
            self.window.contentView().addSubview_(desc_field)
        
        return y - 35
    
    def _add_color_field(self, key: str, label: str, y: int, default: Any, is_temperature: bool = False) -> int:
        """Add a color picker or temperature field."""
        # Label
        label_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, y, 200, 20))
        label_field.setStringValue_(label)
        label_field.setBezeled_(NO)
        label_field.setDrawsBackground_(NO)
        label_field.setEditable_(NO)
        label_field.setSelectable_(NO)
        self.window.contentView().addSubview_(label_field)
        
        if is_temperature:
            # Temperature field (Kelvin)
            temp_field = NSTextField.alloc().initWithFrame_(NSMakeRect(230, y, 80, 24))
            current_value = self.user_config.get(key, default)
            temp_field.setStringValue_(str(current_value))
            self.window.contentView().addSubview_(temp_field)
            self.fields[key] = temp_field
            
            # Description
            desc_field = NSTextField.alloc().initWithFrame_(NSMakeRect(320, y, 260, 20))
            desc_field.setStringValue_("(Color temperature in Kelvin, 2000-9000)")
            desc_field.setBezeled_(NO)
            desc_field.setDrawsBackground_(NO)
            desc_field.setEditable_(NO)
            desc_field.setSelectable_(NO)
            desc_field.setTextColor_(NSColor.grayColor())
            desc_field.setFont_(desc_field.font().fontWithSize_(11))
            self.window.contentView().addSubview_(desc_field)
        else:
            # RGB fields
            current_value = self.user_config.get(key, default)
            if isinstance(current_value, (list, tuple)) and len(current_value) == 3:
                r, g, b = current_value
            else:
                r, g, b = default
            
            # R field
            r_label = NSTextField.alloc().initWithFrame_(NSMakeRect(230, y, 15, 20))
            r_label.setStringValue_("R:")
            r_label.setBezeled_(NO)
            r_label.setDrawsBackground_(NO)
            r_label.setEditable_(NO)
            self.window.contentView().addSubview_(r_label)
            
            r_field = NSTextField.alloc().initWithFrame_(NSMakeRect(250, y, 50, 24))
            r_field.setStringValue_(str(r))
            self.window.contentView().addSubview_(r_field)
            
            # G field
            g_label = NSTextField.alloc().initWithFrame_(NSMakeRect(310, y, 15, 20))
            g_label.setStringValue_("G:")
            g_label.setBezeled_(NO)
            g_label.setDrawsBackground_(NO)
            g_label.setEditable_(NO)
            self.window.contentView().addSubview_(g_label)
            
            g_field = NSTextField.alloc().initWithFrame_(NSMakeRect(330, y, 50, 24))
            g_field.setStringValue_(str(g))
            self.window.contentView().addSubview_(g_field)
            
            # B field
            b_label = NSTextField.alloc().initWithFrame_(NSMakeRect(390, y, 15, 20))
            b_label.setStringValue_("B:")
            b_label.setBezeled_(NO)
            b_label.setDrawsBackground_(NO)
            b_label.setEditable_(NO)
            self.window.contentView().addSubview_(b_label)
            
            b_field = NSTextField.alloc().initWithFrame_(NSMakeRect(410, y, 50, 24))
            b_field.setStringValue_(str(b))
            self.window.contentView().addSubview_(b_field)
            
            self.fields[f"{key}_r"] = r_field
            self.fields[f"{key}_g"] = g_field
            self.fields[f"{key}_b"] = b_field
        
        return y - 35
    
    def _add_slider_field(self, key: str, label: str, y: int, default: int) -> int:
        """Add a slider with label and value display."""
        # Label
        label_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, y, 200, 20))
        label_field.setStringValue_(label)
        label_field.setBezeled_(NO)
        label_field.setDrawsBackground_(NO)
        label_field.setEditable_(NO)
        label_field.setSelectable_(NO)
        self.window.contentView().addSubview_(label_field)
        
        # Slider
        slider = NSSlider.alloc().initWithFrame_(NSMakeRect(230, y, 300, 24))
        current_value = self.user_config.get(key, default)
        slider.setMinValue_(0)
        slider.setMaxValue_(100)
        slider.setIntValue_(int(current_value))
        self.window.contentView().addSubview_(slider)
        
        # Value label
        value_label = NSTextField.alloc().initWithFrame_(NSMakeRect(540, y, 40, 20))
        value_label.setStringValue_(str(int(current_value)))
        value_label.setBezeled_(NO)
        value_label.setDrawsBackground_(NO)
        value_label.setEditable_(NO)
        value_label.setSelectable_(NO)
        self.window.contentView().addSubview_(value_label)
        
        # Connect slider to update label
        slider.setTarget_(self)
        slider.setAction_("sliderChanged:")
        slider.setContinuous_(YES)
        
        self.fields[key] = slider
        self.fields[f"{key}_label"] = value_label
        
        return y - 35
    
    def sliderChanged_(self, sender):
        """Handle slider value changes."""
        # Find which slider was changed and update its label
        for key, field in self.fields.items():
            if field == sender and not key.endswith('_label'):
                label_key = f"{key}_label"
                if label_key in self.fields:
                    self.fields[label_key].setStringValue_(str(int(sender.intValue())))
                break
    
    def _add_buttons(self) -> None:
        """Add Save and Cancel buttons."""
        # Cancel button
        cancel_button = NSButton.alloc().initWithFrame_(NSMakeRect(380, 20, 100, 32))
        cancel_button.setTitle_("Cancel")
        cancel_button.setBezelStyle_(1)
        cancel_button.setTarget_(self)
        cancel_button.setAction_("cancel:")
        self.window.contentView().addSubview_(cancel_button)
        
        # Save button
        save_button = NSButton.alloc().initWithFrame_(NSMakeRect(490, 20, 100, 32))
        save_button.setTitle_("Save")
        save_button.setBezelStyle_(1)
        save_button.setKeyEquivalent_("\r")  # Enter key
        save_button.setTarget_(self)
        save_button.setAction_("save:")
        self.window.contentView().addSubview_(save_button)
        
        # Reset to Defaults button
        reset_button = NSButton.alloc().initWithFrame_(NSMakeRect(20, 20, 140, 32))
        reset_button.setTitle_("Reset to Defaults")
        reset_button.setBezelStyle_(1)
        reset_button.setTarget_(self)
        reset_button.setAction_("reset:")
        self.window.contentView().addSubview_(reset_button)
    
    def save_(self, sender) -> None:
        """Save settings and close window."""
        # Save API credentials to .env
        api_keys = ["GOVEE_API_KEY", "GOVEE_DEVICE_MAC", "GOVEE_MODEL", "GOOGLE_CALENDAR_ID"]
        for key in api_keys:
            if key in self.fields:
                value = self.fields[key].stringValue()
                if value:  # Only save non-empty values
                    set_key(ENV_FILE_PATH, key, value)
        
        # Save user config to JSON
        self.user_config = {}
        
        # Timing
        for key in ["meeting_idle_threshold", "meeting_soon_threshold"]:
            if key in self.fields:
                try:
                    value = int(self.fields[key].stringValue())
                    self.user_config[key] = value
                except ValueError:
                    pass
        
        # Colors (RGB)
        for key in ["color_soon", "color_imminent", "color_in_meeting"]:
            try:
                r = int(self.fields[f"{key}_r"].stringValue())
                g = int(self.fields[f"{key}_g"].stringValue())
                b = int(self.fields[f"{key}_b"].stringValue())
                # Validate RGB range
                if all(0 <= v <= 255 for v in [r, g, b]):
                    self.user_config[key] = [r, g, b]
            except (ValueError, KeyError):
                pass
        
        # Temperature
        if "color_idle_temp" in self.fields:
            try:
                value = int(self.fields["color_idle_temp"].stringValue())
                if 2000 <= value <= 9000:
                    self.user_config["color_idle_temp"] = value
            except ValueError:
                pass
        
        # Brightness
        for key in ["brightness_idle", "brightness_soon", "brightness_imminent", "brightness_in_meeting"]:
            if key in self.fields:
                value = self.fields[key].intValue()
                self.user_config[key] = int(value)
        
        self._save_user_config()
        
        # Close window
        self.window.close()
    
    def cancel_(self, sender) -> None:
        """Cancel and close window without saving."""
        self.window.close()
    
    def reset_(self, sender) -> None:
        """Reset all settings to defaults."""
        # Clear user config
        self.user_config = {}
        self._save_user_config()
        
        # Close and reopen to show defaults
        self.window.close()


def show_settings() -> None:
    """Show the settings window."""
    settings = SettingsWindow()
    settings.show()


def load_user_config() -> Dict[str, Any]:
    """
    Load user configuration.
    
    Returns:
        Dictionary of user configuration values
    """
    if os.path.exists(USER_CONFIG_PATH):
        try:
            with open(USER_CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}