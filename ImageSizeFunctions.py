"""Image dimension and resizing utilities for Folder2WebP.

This module has no GUI dependencies. ImageConverter.py can call these helpers
from CustomTkinter callbacks and during batch conversion.
"""

from __future__ import annotations

from math import floor, gcd, isfinite
from typing import Literal

from PIL import Image, ImageOps


# Labels are suitable for a CustomTkinter CTkOptionMenu.
ASPECT_RATIOS: dict[str, tuple[int, int] | None] = {
    "Original": None,
    "16:9": (16, 9),
    "4:3": (4, 3),
    "3:2": (3, 2),
    "1:1": (1, 1),
    "9:16": (9, 16),
    "2:3": (2, 3),
    "21:9": (21, 9),
    "Custom": None,
}

# Human-readable selections for the GUI, mapped to Pillow resize behaviors.
RESIZE_METHODS = {
    "Stretch / Squash": "stretch",  # Exact dimensions; may distort the source.
    "Crop to Fill": "cover",       # Exact dimensions; center-crops as needed.
    "Fit Without Cropping": "contain",  # Fits inside the box; can be smaller.
}

ResizeMode = Literal["stretch", "contain", "cover"]


def _PositivePixel(Value: int | float | str) -> int:
    """Validate a pixel count (must be a positive whole number)."""
    if isinstance(Value, bool):
        raise ValueError("Pixel dimensions must be positive whole numbers.")
    try:
        Number = float(Value)
    except (TypeError, ValueError, OverflowError) as Error:
        raise ValueError("Pixel dimensions must be positive whole numbers.") from Error
    if not isfinite(Number) or Number < 1 or not Number.is_integer():
        raise ValueError("Pixel dimensions must be positive whole numbers.")
    return int(Number)


def _RoundPixel(Value: float) -> int:
    """Round positive dimensions to the nearest pixel; .5 rounds upward."""
    return max(1, floor(Value + 0.5))


def GetOriginalAspectRatio(Width: int, Height: int) -> tuple[int, int]:
    """Return the source image's aspect ratio, reduced to smallest terms."""
    Width, Height = _PositivePixel(Width), _PositivePixel(Height)
    CommonDivisor = gcd(Width, Height)
    return Width // CommonDivisor, Height // CommonDivisor


def GetAspectRatio(
    RatioName: str,
    OriginalSize: tuple[int, int] | None = None,
) -> tuple[int, int] | None:
    """Resolve a preset, or the source image ratio for 'Original'.

    'Custom' intentionally has no locked ratio and returns None.
    """
    if RatioName not in ASPECT_RATIOS:
        raise ValueError(f"Unknown aspect ratio: {RatioName!r}")
    if RatioName == "Original":
        if OriginalSize is None:
            raise ValueError("OriginalSize is required for the Original aspect ratio.")
        return GetOriginalAspectRatio(*OriginalSize)
    return ASPECT_RATIOS[RatioName]


def CalculateDimensions(
    Width: int | str,
    Height: int | str,
    RatioName: str = "Original",
    OriginalSize: tuple[int, int] | None = None,
    ChangedField: Literal["width", "height"] = "width",
    KeepAspectRatio: bool = True,
) -> tuple[int, int]:
    """Return integer (width, height), optionally locking an aspect ratio.

    The dimension being edited stays unchanged; the other snaps to the
    nearest whole pixel. Non-matching dimensions do NOT select 'Custom'.

    When KeepAspectRatio=False or RatioName='Custom', both entries are kept.
    """
    if ChangedField not in ("width", "height"):
        raise ValueError("ChangedField must be 'width' or 'height'.")

    Ratio = GetAspectRatio(RatioName, OriginalSize) if KeepAspectRatio else None
    if Ratio is None:
        return _PositivePixel(Width), _PositivePixel(Height)

    RatioWidth, RatioHeight = Ratio
    if ChangedField == "width":
        NewWidth = _PositivePixel(Width)
        return NewWidth, _RoundPixel(NewWidth * RatioHeight / RatioWidth)

    NewHeight = _PositivePixel(Height)
    return _RoundPixel(NewHeight * RatioWidth / RatioHeight), NewHeight


def ResizeImage(
    SourceImage: Image.Image,
    Width: int | str,
    Height: int | str,
    ResizeEnabled: bool = True,
    KeepAspectRatio: bool = True,
    RatioName: str = "Original",
    ChangedField: Literal["width", "height"] = "width",
    Mode: ResizeMode = "stretch",
) -> Image.Image:
    """Return a resized Pillow image; leave the source image untouched.

    With a locked ratio, output dimensions are calculated against each source
    image independently (important when a folder mixes portrait/landscape).

    Mode='stretch' fills the exact requested dimensions, potentially distorting
    the source when using a different ratio. Mode='contain' fits inside the
    requested box without distortion and may produce smaller dimensions.
    Mode='cover' fills the box by cropping without distortion.
    """
    if not ResizeEnabled:
        return SourceImage.copy()

    OutputWidth, OutputHeight = CalculateDimensions(
        Width=Width,
        Height=Height,
        RatioName=RatioName,
        OriginalSize=SourceImage.size,
        ChangedField=ChangedField,
        KeepAspectRatio=KeepAspectRatio,
    )
    TargetSize = (OutputWidth, OutputHeight)
    if Mode == "stretch":
        return SourceImage.resize(TargetSize, Image.Resampling.LANCZOS)
    if Mode == "contain":
        return ImageOps.contain(SourceImage, TargetSize, method=Image.Resampling.LANCZOS)
    if Mode == "cover":
        return ImageOps.fit(SourceImage, TargetSize, method=Image.Resampling.LANCZOS)
    raise ValueError("Mode must be 'stretch', 'contain', or 'cover'.")
