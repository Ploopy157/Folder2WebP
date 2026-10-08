FOLDER2WEBP — MAC DISTRIBUTION GUIDE
==================================
Convert, compress, and optionally resize a folder of images to WebP.

CHOOSE YOUR DOWNLOAD
--------------------
Open Apple menu > About This Mac.
- If it shows an Apple M-series chip, choose the macOS-arm64 ZIP.
- If it shows an Intel processor, choose the macOS-x86_64 ZIP.

The release is built for one processor architecture, not as a universal app.
Use the Mac build on macOS. Windows .exe files will not run directly on macOS.

QUICK START
-----------
1. Download the matching Mac ZIP.
2. Double-click the ZIP in Finder to extract it on your Mac.
3. Move Folder2WebP-<version>.app to Applications, or to a folder you own.
   For example: Folder2WebP-1.3.1.app.
4. Double-click the app to launch it.

Python, pip, and developer tools are not required.

Keep the .app bundle intact. It contains everything the application needs.
Share the original ZIP rather than copying individual files from inside
the app bundle. Extract it on macOS to preserve its structure.

FIRST-LAUNCH SECURITY PROMPT
----------------------------
This build is not Developer ID signed or notarized. macOS may say the
developer cannot be verified or that Apple cannot check the app.

If you trust the release source and want to open it:
1. Attempt to open the app and dismiss the warning.
2. Open Apple menu > System Settings > Privacy & Security.
3. Scroll to the security section and locate the message for Folder2WebP.
4. Click Open Anyway, authenticate if requested, and confirm Open.

Availability and wording can vary by macOS version and company policy.
If the control is unavailable on a managed computer, contact your IT team.
A damaged-app or malware warning is a different issue: download a fresh
copy from the trusted release source and report the exact message if it
persists.

Apple's opening guidance:
https://support.apple.com/102445

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

TROUBLESHOOTING ON MAC
----------------------
- App is incompatible: check that the download matches the processor in
  About This Mac. Include your macOS version when reporting an issue.
- App is damaged or will not open: download and extract a fresh ZIP directly
  on the Mac. Preserve the entire .app bundle and record the exact warning.
- Cannot access images or save output: choose a folder you can write to.
  If macOS asks for access to your selected folder, allow it if intended.
- Some images fail: check the final summary. A file may be damaged or use
  an encoding unsupported by the packaged image library.
- Files seem missing: check the selected output location and duplicate
  filename stems.
- Output is larger than expected: resize images or adjust quality/size
  settings; the target stops at minimum quality.

Files named ._Folder2WebP... or a __MACOSX folder may appear when a Mac ZIP
is viewed on another operating system. They hold Mac metadata and are not
the application. Launch the actual Folder2WebP-<version>.app on the Mac.

SETTINGS, UPDATES, AND REMOVAL
-----------------------------
Settings are remembered in:
~/Library/Application Support/ImageConverter/Settings.json

To reset settings:
1. Close Folder2WebP.
2. In Finder, choose Go > Go to Folder.
3. Enter ~/Library/Application Support/ImageConverter
4. Delete Settings.json. Defaults return on the next launch.

To update, close the app and replace it with the app from the new ZIP.
Saved preferences remain available.

To remove the app, close it and move it to the Trash.
Optionally delete the ImageConverter settings folder above.
Converted images remain wherever you saved them.

