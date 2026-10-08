FOLDER2WEBP — WINDOWS DISTRIBUTION GUIDE
======================================
Convert, compress, and optionally resize a folder of images to WebP.

QUICK START
-----------
1. Right-click the downloaded ZIP and choose Extract All.
2. Choose a destination and click Extract.
3. Open the extracted folder.
4. Double-click Folder2WebP-<version>.exe.
   For example: Folder2WebP-1.3.1.exe.

Python, pip, and developer tools are not required. No installer is needed.
Run the extracted executable rather than opening it from inside the ZIP.
The first launch may take a moment while bundled files are unpacked.

Use the Windows build on Windows. Mac application bundles will not run on
Windows. If a work computer blocks the application, contact your IT team
and provide the project link and the exact message.

USING FOLDER2WEBP
----------------
1. Click Browse beside Input Directory and select the folder of source images.
2. Choose where converted images should be saved:
   - Create New Folder: enter a name such as WebP. This creates the output
     folder BESIDE the input folder, rather than inside it.
   - Save to Existing Folder: browse to your chosen destination.
   The input and output folders must be different.
3. Set Start Quality between 0 and 100. Higher values usually give larger files.
4. Optionally enable the file-size target or image resizing.
5. Optionally add plain text before or after each output filename.
6. Click Convert Images. Leave the app open until the final summary appears.
7. Open the output folder to review the converted images.

Only supported images directly inside the input folder are processed.
Subfolders are not scanned. Supported extensions are JPG/JPEG, PNG, WebP,
BMP, GIF, TIF/TIFF, and AVIF; support depends on the packaged image library.
Transparency is preserved when the source image contains it.

FILE SIZE AND COMPRESSION
-------------------------
"Enforce maximum file size" enables repeated compression attempts:
- Maximum File Size (KB): desired size; 1 KB means 1,024 bytes.
- Minimum Quality: lowest permitted quality, no higher than Start Quality.
- Quality Decrement: quality reduction per attempt; must be greater than 0.
- Compression Method: 0 is fastest; 6 spends more time on compression.

The size target is BEST EFFORT. If the file still exceeds the target at
minimum quality, it is saved anyway. Reduce dimensions, lower minimum
quality, or increase the size target if needed.

With the size checkbox off, the app encodes once at Start Quality.
A quality decrement of 1 can require many attempts, especially for large
images. Conversion may take time.

RESIZING
--------
Enable Resize Images and enter positive whole-number pixel dimensions.
- Original + Keep Aspect Ratio: each source image retains its proportions.
  The dimension last edited determines the other dimension for each image.
  The displayed preview is based on the first readable source image.
- Preset ratio + Keep Aspect Ratio: editing one dimension updates the other.
- Custom: width and height can be edited independently.

Choose a resize method:
- Stretch / Squash: fills the calculated dimensions; may distort the image.
- Crop to Fill: preserves proportions and center-crops to fill the dimensions.
- Fit Without Cropping: keeps the full image inside the requested box.
  Output may be smaller than the box; no padding is added.

Resizing takes place before compression.

FILENAMES AND EXISTING OUTPUT
----------------------------
An input named photo.jpg becomes photo.webp.
For example, start text "site-" and end text "-small" produce
site-photo-small.webp.

Use plain filename text. Do not enter folder paths or separators such as
/ or \ in filename additions.

IMPORTANT: Existing output files are replaced WITHOUT confirmation.
Also, photo.jpg and photo.png both produce photo.webp, so one result replaces
the other. Use unique source filename stems or separate output folders.

OTHER CURRENT LIMITATIONS
-------------------------
- Animated images are converted to a single still frame.
- EXIF orientation is not applied automatically. Rotate affected photos
  before conversion if they appear sideways.
- Source metadata, including EXIF and color profiles, is not explicitly
  copied into the output.
- Individual file failures are reported, and remaining files continue.
  Check the final converted/failed counts and review the output folder.

HELP AND SOURCE CODE
--------------------
Project: https://github.com/Ploopy157/Folder2WebP
Report issues: https://github.com/Ploopy157/Folder2WebP/issues

When reporting a problem, include the application version, operating system,
exact error message, and conversion settings. Share a sample image only if
it contains no private information.

LICENSE
-------
Created by Nathan Taylor.
Original application code is licensed under the MIT License.
Third-party dependencies retain their own licenses.
See the accompanying license and third-party notices supplied with the release.

TROUBLESHOOTING ON WINDOWS
-------------------------
- App does not open: confirm the ZIP was fully extracted, then try the
  executable again. Record any Windows or antivirus message for support.
- Cannot save images: choose a folder you can write to and verify that
  output files are not locked by another program.
- Some images fail: check the final summary. A file may be damaged or use
  an encoding unsupported by the packaged image library.
- Files seem missing: check the selected output location and duplicate
  filename stems.
- Output is larger than expected: the size target stops at minimum quality.
  Resize the images or adjust the quality/size settings.

SETTINGS, UPDATES, AND REMOVAL
-----------------------------
Settings are remembered in:
%LOCALAPPDATA%\ImageConverter\Settings.json

To reset settings:
1. Close Folder2WebP.
2. Press Windows + R, enter %LOCALAPPDATA%\ImageConverter, and press Enter.
3. Delete Settings.json. Defaults return on the next launch.

To update, close the app and extract the new release into a fresh folder.
Saved preferences remain available.

To remove the app, close it and delete its extracted executable/folder.
Optionally delete the ImageConverter settings folder above.
Converted images remain wherever you saved them.

