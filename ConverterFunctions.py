from PIL import Image
import os as Os
from io import BytesIO
from ImageSizeFunctions import ResizeImage, ASPECT_RATIOS, RESIZE_METHODS

ImageExtensions = {
        ".jpg", ".jpeg", ".png", ".webp",
        ".bmp", ".gif", ".tif", ".tiff",
        ".avif"
    }

def GetFilesInDirectory(Path):
    if not Os.path.isdir(Path):
        return []
    return [
        File
        for File in Os.listdir(Path)
        if Os.path.isfile(Os.path.join(Path, File))
        and Os.path.splitext(File)[1].lower() in ImageExtensions
    ]

def PrepareImage(Img):
    # Preserve transparency when the source image has an alpha channel.
    if "A" in Img.getbands() or "transparency" in Img.info:
        return Img.convert("RGBA")

    # Standard RGB conversion for images without transparency.
    return Img.convert("RGB")

def DecrementQuality(
    Img,
    StartingQuality,
    Decrement,
    MinimumQuality,
    MaximumBytes,
    CompressionMethod
):
    CurrentQuality = StartingQuality

    while True:
        # Create a fresh memory buffer for this attempt.
        with BytesIO() as Buffer:
            Img.save(
                Buffer,
                format="WEBP",
                quality=CurrentQuality,
                method=CompressionMethod
            )

            # Get the complete encoded WebP as bytes.
            ImageBytes = Buffer.getvalue()

        # None means maximum-size checking is disabled.
        if MaximumBytes is None or len(ImageBytes) <= MaximumBytes:
            return ImageBytes, CurrentQuality

        # Save at minimum quality even if the image exceeds the size target.
        if CurrentQuality == MinimumQuality:
            return ImageBytes, CurrentQuality

        # Release the rejected bytes before encoding the next attempt.
        del ImageBytes

        # Reduce quality without going below the minimum.
        CurrentQuality = max(MinimumQuality, CurrentQuality - Decrement)

def ConvertFolder(
    InputDirectory,
    FinishedFolderName,
    MaxFileSize,
    DoMaxSizeCheck,
    StartQuality,
    MinimumQuality,
    QualityDecrement,
    CompressionMethod,
    FileNameAdditionStart,
    FileNameAdditionEnd,
    Report=print,
    ReportProgress=None,
    OutputDirectory=None,
    ResizeEnabled=False,
    KeepAspectRatio=True,
    RatioName="Original",
    ResizeWidth=1200,
    ResizeHeight=800,
    ChangedField="width",
    ResizeMethod="Stretch / Squash"
):
    #Validate input parameters
    if not 0 <= StartQuality <= 100:
        raise ValueError("StartQuality must be between 0 and 100.")

    if ResizeEnabled:
        if ResizeMethod not in RESIZE_METHODS:
            raise ValueError("Unknown image resize method.")
        if RatioName not in ASPECT_RATIOS:
            raise ValueError("Unknown aspect ratio preset.")
        if int(ResizeWidth) < 1 or int(ResizeHeight) < 1:
            raise ValueError("Image dimensions must be positive integers.")

    MaximumBytes = None

    if DoMaxSizeCheck:
        if not 0 <= MinimumQuality <= StartQuality:
            raise ValueError("MinimumQuality must be between 0 and StartQuality.")

        if QualityDecrement <= 0:
            raise ValueError("QualityDecrement must be greater than 0.")

        if MaxFileSize <= 0:
            raise ValueError("MaxFileSize must be greater than 0.")

        MaximumBytes = int(MaxFileSize * 1024)

    
    Count = 0
    TotalSize = 0
    FailedCount = 0
    #Select the parent directory of the starting directory.
    if OutputDirectory is None:
        # Create the named folder beside the input folder.
        FinalDirectory = Os.path.join(
            Os.path.dirname(InputDirectory),
            FinishedFolderName
        )
        Os.makedirs(FinalDirectory, exist_ok=True)
    else:
        # Save directly into the selected existing folder.
        if not Os.path.isdir(OutputDirectory):
            raise ValueError("The selected output folder does not exist.")

        FinalDirectory = OutputDirectory

    
    #Compress/create the image files
    Files = GetFilesInDirectory(InputDirectory)
    TotalFiles = len(Files)

    if ReportProgress is not None:
        ReportProgress(0, TotalFiles)

    for FileName in Files:
        try:
            InputPath = Os.path.join(InputDirectory, FileName)

            with Image.open(InputPath) as Img:
                
                NewName = (
                    FileNameAdditionStart
                    + Os.path.splitext(FileName)[0]
                    + FileNameAdditionEnd
                    + ".webp"
                )

                OutputPath = Os.path.join(FinalDirectory, NewName)
                OldSize = Os.path.getsize(InputPath)

                # Prepare as RGB or RGBA so transparency survives WebP export.
                # The context manager closes this intermediate image afterward.
                with PrepareImage(Img) as PreparedImage:
                    # Resizing creates another Pillow image when enabled.
                    if ResizeEnabled:
                        ProcessedImage = ResizeImage(
                            PreparedImage, ResizeWidth, ResizeHeight,
                            ResizeEnabled=True,
                            KeepAspectRatio=KeepAspectRatio,
                            RatioName=RatioName,
                            ChangedField=ChangedField,
                            Mode=RESIZE_METHODS[ResizeMethod]
                        )
                    else:
                        ProcessedImage = PreparedImage

                    try:
                        # Compress the FINAL image (resized when enabled).
                        ImageBytes, CurrentQuality = DecrementQuality(
                            ProcessedImage,
                            StartQuality,
                            QualityDecrement,
                            MinimumQuality,
                            MaximumBytes,
                            CompressionMethod
                        )
                    finally:
                        # Close the resized copy, if one was created.
                        # PreparedImage is closed by its own 'with' block.
                        if ProcessedImage is not PreparedImage:
                            ProcessedImage.close()

                with open(OutputPath, "wb") as OutputFile:
                    OutputFile.write(ImageBytes)

                NewSize = len(ImageBytes)
                Count += 1
                TotalSize += NewSize

                SizeNotice = ""

                if MaximumBytes is not None and NewSize > MaximumBytes:
                    SizeNotice = (
                        f" — exceeds {MaxFileSize} KB target; "
                        f"saved at minimum quality."
                    )

                Report(
                    f"Converted {FileName} ({round(OldSize / 1024)} KB) "
                    f"to: {NewName} "
                    f"({CurrentQuality}% / {round(NewSize / 1024)} KB)"
                    f"{SizeNotice}"
                )

        except Exception as Error:
            FailedCount += 1

            Report(
                f"Failed {FileName}: "
                f"{type(Error).__name__}: {Error}"
            )

        finally:
            if ReportProgress is not None:
                ReportProgress(Count, TotalFiles)

    Report(
        f"Finished: {Count} converted, "
        f"{FailedCount} failed. "
        f"Total output size: {round(TotalSize / 1024)} KB."
    )
#EOF