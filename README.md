# Folder2WebP

Folder2WebP is a desktop utility for converting a folder of images to WebP. It includes adjustable compression, optional resizing, filename additions, and remembered settings.

Created by Nathan Taylor as a personal project to make routine image preparation faster.

## Features

- Convert JPG/JPEG, PNG, WebP, BMP, GIF, TIF/TIFF, and AVIF images.
- Preserve transparency when the source image contains it.
- Choose a new output folder beside the input folder or an existing output folder.
- Adjust WebP quality and compression effort.
- Reduce quality toward a file-size target.
- Resize using original, preset, or custom aspect ratios.
- Choose Stretch / Squash, Crop to Fill, or Fit Without Cropping.
- Add text before or after output filenames.
- Remember settings between sessions.

Format support depends on the installed Pillow build, including its AVIF and WebP support.

## Run from source

### Requirements

- Python 3.14, the project's current development version.
- Tkinter support in your Python installation.
- Dependencies listed in `requirements.txt`.

Windows and macOS build scripts are included. Build each packaged application on its corresponding operating system.

### Get the project

Clone the repository:

```sh
git clone https://github.com/Ploopy157/Folder2WebP.git
cd Folder2WebP
```

Alternatively, select **Code → Download ZIP** on GitHub, extract the archive, and open a terminal in the extracted project folder.

### Windows setup

Run these commands in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ImageConverter.py
```

If `python` is unavailable but the Python launcher is installed, use `py -3.14 -m venv .venv` for the first command.

These commands use the virtual environment directly, so PowerShell activation is unnecessary.

### macOS setup

Run these commands in Terminal:

```sh
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python ImageConverter.py
```

Check `python3 --version` first to confirm you are using the intended Python installation. If Tkinter is unavailable, use a Python installation that includes working Tkinter support.

## Convert images

1. Launch the application.
2. Select the **Input Directory** containing your images.
3. Choose where to save the converted images:
   - **Create New Folder:** enter a folder name. The output folder is created beside the input folder. For example, an input folder of `Pictures/Originals` and a finished folder name of `WebP` produces `Pictures/WebP`.
   - **Save to Existing Folder:** browse to an existing destination.
4. Set **Start Quality**, from 0 to 100.
5. Configure the optional file-size and resizing settings below.
6. Enter optional filename additions.
7. Select **Convert Images** and wait for the final summary.

The output folder must differ from the input folder. Only supported files directly inside the input folder are processed; subfolders are not scanned.

### Quality and file size

| Setting | Meaning |
|---|---|
| Start Quality | Initial WebP quality, from 0 to 100. Higher values usually produce larger files. |
| Enforce maximum file size | Enables repeated encoding at lower quality to try to meet the size target. |
| Maximum File Size (KB) | Target output size. The application treats 1 KB as 1,024 bytes. |
| Minimum Quality | Lowest quality the application will use. Must be between 0 and Start Quality. |
| Quality Decrement | Amount by which quality decreases on each attempt. Must be greater than zero. |
| Compression Method | Encoding effort, from 0 to 6. Zero is fastest; six uses more effort and takes longer. |

**The file-size target is best effort.** If the image still exceeds the target at minimum quality, it is saved at minimum quality and reported as exceeding the target.

Turn off the size-limit checkbox to encode once at Start Quality. A quality decrement of 1 gives fine control but may require many encoding attempts.

### Resize images

Enable **Resize Images**, then choose dimensions, an aspect ratio, and a resize method.

- **Original:** when Keep Aspect Ratio is enabled, each image uses its own original proportions. The dimension last edited determines the other dimension for each source image. The displayed preview uses the first readable image in the selected folder.
- **Preset ratios:** choose a ratio such as 16:9, 4:3, 1:1, or 9:16. With Keep Aspect Ratio enabled, editing one dimension updates the other.
- **Custom:** width and height are independent. Selecting Custom turns off Keep Aspect Ratio.

Dimensions must be positive whole pixel counts.

| Resize method | Result |
|---|---|
| Stretch / Squash | Uses the calculated target dimensions exactly. Images may be distorted when their proportions differ from the target. |
| Crop to Fill | Preserves source proportions and crops from the center to fill the target dimensions. |
| Fit Without Cropping | Preserves source proportions and fits the entire image inside the target dimensions. Output may be smaller than the requested box; no padding is added. |

Resizing happens before WebP compression.

### Filename additions

Output files use this naming pattern:

```text
[start addition][original filename without extension][end addition].webp
```

For example, `photo.jpg` with a start addition of `site-` and an end addition of `-small` becomes `site-photo-small.webp`.

Use plain filename text for additions. Do not enter paths or folder separators.

## Current limitations

- Existing output files are overwritten without confirmation.
- Inputs with the same filename stem, such as `photo.jpg` and `photo.png`, produce the same output name. Only the last written result remains. Use distinct stems or separate conversion runs and output folders.
- Filename additions are not currently validated against path separators. Use plain text to keep output in the selected folder.
- Animated images are exported as a single still frame.
- EXIF orientation is not currently applied before conversion. Rotate affected images before converting.
- Source metadata, such as EXIF and ICC profiles, is not explicitly carried into output files.
- Individual file failures are reported, and processing continues with the remaining images.

## Build a Windows executable

Set up the Windows virtual environment and install dependencies as described above.

From PowerShell in the project folder, run:

```powershell
.\Build_Windows.bat
```

The script activates `.venv` when it exists and uses PyInstaller to bundle Python, the application, CustomTkinter assets, and the icons.

It reads `ProgramVersion` from `Version.py`. For version 1.3.1, the output is:

```text
dist/Folder2WebP-1.3.1.exe
```

Close any running copy of the executable before rebuilding. The packaged executable can run without a separate Python installation.

## Build a macOS application

Set up the macOS virtual environment and install dependencies as described above. The build script requires `.venv/bin/python`.

Run:

```sh
bash Build_Mac.command
```

To allow launching the script directly, including from Finder, first run:

```sh
chmod +x Build_Mac.command
```

The script reads the version from `Version.py`, builds for the architecture of the Python interpreter used, and creates both an application bundle and a ZIP archive.

For version 1.3.1 on Apple Silicon, the outputs are:

```text
dist/Folder2WebP-1.3.1.app
dist/Folder2WebP-1.3.1-macOS-arm64.zip
```

An Intel Python interpreter produces an `x86_64` archive instead. This script does not build a universal application.

Share the generated ZIP to preserve the application bundle's symbolic links and metadata. Recipients should extract it on macOS. The packaged application includes Python.

The script does not configure Developer ID signing or notarization. macOS may display a security warning for a downloaded build.

## Settings

Settings are stored outside the project folder:

| Platform | Location |
|---|---|
| Windows | `%LOCALAPPDATA%\ImageConverter\Settings.json` |
| macOS | `~/Library/Application Support/ImageConverter/Settings.json` |

To reset preferences, close the application and delete `Settings.json`. Defaults are used the next time the application starts.

## Project files

| File | Purpose |
|---|---|
| `ImageConverter.py` | Application launcher |
| `ConverterGUI.py` | Graphical interface and conversion worker coordination |
| `ConverterFunctions.py` | File discovery, image preparation, and WebP compression |
| `ImageSizeFunctions.py` | Aspect ratios, dimension calculations, and resizing |
| `Settings.py` | Saved preferences and color settings |
| `Version.py` | Application version and change notes |
| `Build_Windows.bat` | Windows PyInstaller build |
| `Build_Mac.command` | macOS PyInstaller build and ZIP packaging |
| `Icon.png` / `Icon.ico` | Application icon assets |
| `requirements.txt` | Python dependencies |

Generated `build/`, `dist/`, virtual environments, and Python caches are excluded by `.gitignore`. Packaged downloads can be distributed through GitHub Releases.

## Troubleshooting

- **PyInstaller is not recognized:** install dependencies into the project virtual environment and run the included build script. It invokes PyInstaller through Python.
- **Windows build reports access denied:** close the running executable, then try again.
- **macOS builder cannot find Python:** create `.venv` in the project folder using the macOS setup instructions.
- **An image fails to convert:** check the reported error and confirm that Pillow can open the format. An extension alone does not guarantee a valid image.
- **An image remains above the size target:** lower Minimum Quality, resize the image, or increase the target size.
- **An output image is missing:** check for duplicate filename stems or an existing output file with the same name.

## License

Folder2WebP's original code is available under the [MIT License](LICENSE).

Third-party dependencies retain their own licenses. Include any notices required by those dependencies when distributing packaged builds.

