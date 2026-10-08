#!/bin/bash
# Keep this file beside ImageConverter.py and Version.py.
set -e

Finish() {
    ExitCode=$?
    trap - EXIT
    if [ "$ExitCode" -ne 0 ]; then
        echo
        echo "Build failed. Review the error messages above."
    fi
    if [ -t 0 ]; then
        read -r -p "Press Return to close..." || true
    fi
    exit "$ExitCode"
}
trap Finish EXIT

# Run from the project folder, including when opened from Finder.
cd "$(dirname "$0")"
PythonPath="$PWD/.venv/bin/python"

# Reuse the working project environment instead of Apple's Python.
if [ ! -x "$PythonPath" ]; then
    echo "Cannot find the project's .venv/bin/python."
    echo "Create the Mac virtual environment in this folder first."
    exit 1
fi

Version=$("$PythonPath" -c "from Version import ProgramVersion; print(ProgramVersion)")
if [ -z "$Version" ]; then
    echo "ProgramVersion in Version.py must not be empty."
    exit 1
fi
Architecture=$("$PythonPath" -c "import platform as Platform; print(Platform.machine())")
case "$Architecture" in
    arm64|x86_64) ;;
    *) echo "Unsupported Mac architecture: $Architecture"; exit 1 ;;
esac

AppName="Folder2WebP-$Version"
echo "Building $AppName for $Architecture..."

"$PythonPath" -m PyInstaller \
    --clean \
    --noconfirm \
    --onedir \
    --windowed \
    --target-arch "$Architecture" \
    --collect-all customtkinter \
    --name "$AppName" \
    --icon "$PWD/Icon.png" \
    --add-data "$PWD/Icon.png:." \
    --specpath "$PWD/build" \
    "ImageConverter.py"

# Preserve the application bundle's symbolic links and metadata for sharing.
ArchivePath="dist/$AppName-macOS-$Architecture.zip"
ditto -c -k --sequesterRsrc --keepParent "dist/$AppName.app" "$ArchivePath"

echo
echo "Build complete: $PWD/dist/$AppName.app"
echo "Share this ZIP: $PWD/$ArchivePath"
