import json as Json
import os as Os
import sys as Sys

# Defaults used when a saved color is missing or invalid.
DefaultColors = {
    "BackgroundColor": "#151922",
    "TextColor": "#CCCCCC",
    "InputColor": "#232B38",
    "BorderColor": "#3A4658",
    "ButtonColor": "#2563EB",
    "ButtonHoverColor": "#3B82F6",
    "ButtonPressedColor": "#1D4ED8",
    "ButtonTextColor": "#FFFFFF",
    "MutedTextColor": "#8D99AE"
}


if Sys.platform == "darwin":
    # macOS application settings.
    SettingsDirectory = Os.path.join(
        Os.path.expanduser("~"),
        "Library",
        "Application Support",
        "ImageConverter"
    )
else:
    # Windows application settings.
    LocalAppData = Os.environ.get("LOCALAPPDATA") or Os.path.join(
        Os.path.expanduser("~"), "AppData", "Local"
    )

    SettingsDirectory = Os.path.join(
        LocalAppData, "ImageConverter"
    )

SettingsPath = Os.path.join(SettingsDirectory, "Settings.json")


def LoadSettings():
    try:
        with open(SettingsPath, "r", encoding="utf-8") as SettingsFile:
            SavedSettings = Json.load(SettingsFile)

        # Settings must be a dictionary of names and values.
        return SavedSettings if isinstance(SavedSettings, dict) else {}

    except (OSError, ValueError):
        # Missing, unreadable, or malformed settings use the defaults.
        return {}

def LoadColors(SavedSettings):
    # Copy the defaults so we don't modify the original dictionary.
    Colors = DefaultColors.copy()
    SavedColors = SavedSettings.get("Colors", {})

    if isinstance(SavedColors, dict):
        for ColorName in DefaultColors:
            ColorValue = SavedColors.get(ColorName)

            # Accept colors in the six-digit hexadecimal format.
            if (
                isinstance(ColorValue, str)
                and len(ColorValue) == 7
                and ColorValue.startswith("#")
                and all(
                    Character in "0123456789abcdefABCDEF"
                    for Character in ColorValue[1:]
                )
            ):
                Colors[ColorName] = ColorValue

    return Colors


def SaveSettings(CurrentSettings):
    Os.makedirs(SettingsDirectory, exist_ok=True)

    # Finish writing a temporary file before replacing saved settings.
    TemporaryPath = SettingsPath + ".tmp"

    with open(TemporaryPath, "w", encoding="utf-8") as SettingsFile:
        Json.dump(CurrentSettings, SettingsFile, indent=4)

    Os.replace(TemporaryPath, SettingsPath)