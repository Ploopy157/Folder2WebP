# Folder2WebP graphical interface.
from pathlib import Path
import sys as Sys
import os as Os
import tkinter as Tk
from tkinter import ttk as Ttk
from tkinter import filedialog as FileDialog, messagebox as MessageBox
from threading import Thread
from queue import Queue, Empty
from PIL import Image
import customtkinter as CTk
from ConverterFunctions import ConvertFolder, GetFilesInDirectory
from ImageSizeFunctions import ASPECT_RATIOS, CalculateDimensions, RESIZE_METHODS
from Settings import LoadSettings, LoadColors, SaveSettings
from Version import ProgramVersion as VersionNumber

# Default conversion options (overridden by saved settings).
Directory = ""
FinishedFolderName = "WebP"
OutputMode = "Create New Folder"
ExistingOutputDirectory = ""
MaxFileSize = 200
DoMaxSizeCheck = True
StartQuality = 100
MinimumQuality = 40
QualityDecrement = 1
CompressionMethod = 6
FileNameAdditionStart = ""
FileNameAdditionEnd = ""

class ConverterGUI(CTk.CTk):
    def BrowseDirectory(self, ParentWindow, DirectoryVariable, DialogTitle="Select the folder containing your images"):
        SelectedDirectory = FileDialog.askdirectory(parent=ParentWindow, title=DialogTitle, mustexist=True)
        if SelectedDirectory:
            DirectoryVariable.set(SelectedDirectory)
            self.UpdateResizeDimensions()

    def ToggleOutputControls(self, OutputModeVariable, NewFolderFrame, ExistingFolderFrame):
        NewFolderFrame.pack_forget()
        ExistingFolderFrame.pack_forget()
        if OutputModeVariable.get() == "Save to Existing Folder":
            ExistingFolderFrame.pack(fill="x", pady=(10, 0))
        else:
            NewFolderFrame.pack(fill="x", pady=(10, 0))

    def ToggleSizeControls(self, DoMaxSizeCheckVariable, SizeFieldsFrame):
        if DoMaxSizeCheckVariable.get():
            SizeFieldsFrame.pack(fill="x", pady=(10, 0))
        else:
            SizeFieldsFrame.pack_forget()

    def RememberSettings(self):
        # Keep the entered text, including values in hidden size fields.
        CurrentSettings = {
            "InputDirectory": self.DirectoryVariable.get(),
            "FinishedFolderName": self.FinishedFolderNameVariable.get(),
            "OutputMode": self.OutputModeVariable.get(),
            "ExistingOutputDirectory": self.ExistingOutputDirectoryVariable.get(),
            "MaxFileSize": self.MaxFileSizeVariable.get(),
            "DoMaxSizeCheck": self.DoMaxSizeCheckVariable.get(),
            "StartQuality": self.StartQualityVariable.get(),
            "MinimumQuality": self.MinimumQualityVariable.get(),
            "QualityDecrement": self.QualityDecrementVariable.get(),
            "CompressionMethod": self.CompressionMethodVariable.get(),
            "FileNameAdditionStart": self.FileNameAdditionStartVariable.get(),
            "FileNameAdditionEnd": self.FileNameAdditionEndVariable.get(),
            "ResizeEnabled": self.ResizeEnabledVariable.get(),
            "KeepAspectRatio": self.KeepAspectRatioVariable.get(),
            "RatioName": self.RatioNameVariable.get(),
            "ResizeWidth": self.ResizeWidthVariable.get(),
            "ResizeHeight": self.ResizeHeightVariable.get(),
            "ChangedField": self.LastDimensionChanged,
            "ResizeMethod": self.ResizeMethodVariable.get(),
            "Colors": self.Colors,
        }

        try:
            SaveSettings(CurrentSettings)
        except OSError as Error:
            MessageBox.showwarning(
                "Settings Not Saved",
                f"Your settings could not be saved:\n{Error}",
                parent=self.Root
            )


    def CloseWindow(self):
        self.RememberSettings()
        self.Root.destroy()

    def StartConversion(self):
        try:
            SelectedDirectory = self.DirectoryVariable.get().strip()

            if not Os.path.isdir(SelectedDirectory):
                raise ValueError("Select an existing input directory.")
            # Normalize the input path before calculating its parent folder.
            SelectedDirectory = Os.path.abspath(SelectedDirectory)

            SelectedDoMaxSizeCheck = self.DoMaxSizeCheckVariable.get()

            # Read the controls once so this run uses consistent settings.
            SelectedSettings = {
                "InputDirectory": SelectedDirectory,
                "FinishedFolderName": self.FinishedFolderNameVariable.get(),
                "OutputDirectory": None,
                "MaxFileSize": (
                    float(self.MaxFileSizeVariable.get())
                    if SelectedDoMaxSizeCheck else 0
                ),
                "DoMaxSizeCheck": SelectedDoMaxSizeCheck,
                "StartQuality": int(self.StartQualityVariable.get()),
                "MinimumQuality": (
                    int(self.MinimumQualityVariable.get())
                    if SelectedDoMaxSizeCheck else 0
                ),
                "QualityDecrement": (
                    int(self.QualityDecrementVariable.get())
                    if SelectedDoMaxSizeCheck else 1
                ),
                "CompressionMethod": int(self.CompressionMethodVariable.get()),
                "FileNameAdditionStart": self.FileNameAdditionStartVariable.get(),
                "FileNameAdditionEnd": self.FileNameAdditionEndVariable.get(),
                "ResizeEnabled": self.ResizeEnabledVariable.get(),
                "KeepAspectRatio": self.KeepAspectRatioVariable.get(),
                "RatioName": self.RatioNameVariable.get(),
                "ResizeWidth": self.ResizeWidthVariable.get(),
                "ResizeHeight": self.ResizeHeightVariable.get(),
                "ChangedField": self.LastDimensionChanged,
                "ResizeMethod": self.ResizeMethodVariable.get()
            }

            if SelectedSettings["ResizeEnabled"]:
                if not SelectedSettings["ResizeWidth"].isdigit() or not SelectedSettings["ResizeHeight"].isdigit() or int(SelectedSettings["ResizeWidth"]) < 1 or int(SelectedSettings["ResizeHeight"]) < 1:
                    raise ValueError("Image width and height must be positive pixel counts.")
                if SelectedSettings["ResizeMethod"] not in RESIZE_METHODS:
                    raise ValueError("Choose a valid image resize method.")
                if SelectedSettings["RatioName"] not in ASPECT_RATIOS:
                    raise ValueError("Select a valid aspect ratio.")

            if self.OutputModeVariable.get() == "Save to Existing Folder":
                SelectedOutputDirectory = (
                    self.ExistingOutputDirectoryVariable.get().strip()
                )

                if not Os.path.isdir(SelectedOutputDirectory):
                    raise ValueError("Select an existing output folder.")

                OutputDirectory = Os.path.abspath(SelectedOutputDirectory)
                SelectedSettings["OutputDirectory"] = OutputDirectory

            else:
                FolderName = SelectedSettings["FinishedFolderName"].strip()

                if not FolderName or FolderName in (".", ".."):
                    raise ValueError("Enter a finished folder name.")

                if any(Character in '<>:"/\\|?*' for Character in FolderName):
                    raise ValueError(
                        "The finished folder name contains invalid characters."
                    )

                SelectedSettings["FinishedFolderName"] = FolderName

                OutputDirectory = Os.path.join(
                    Os.path.dirname(SelectedDirectory),
                    FolderName
                )

            # Apply the existing input/output separation rule to both modes.
            InputFolderPath = Os.path.normcase(
                Os.path.realpath(SelectedDirectory)
            )
            OutputFolderPath = Os.path.normcase(
                Os.path.realpath(OutputDirectory)
            )

            if OutputFolderPath == InputFolderPath:
                raise ValueError(
                    "The output folder must differ from the input folder."
                )

        except ValueError as Error:
            self.StatusVariable.set("Check your settings")
            MessageBox.showerror("Invalid Settings", str(Error), parent=self.Root)
            return

        self.RememberSettings()
        self.StatusVariable.set("Converting...")
        self.FileCountVariable.set("0/0 files converted")
        self.ConvertButton.configure(state="disabled")

        # The worker reports its result here without changing Tk widgets.
        ResultQueue = Queue()

        def ReportStatus(Message):
            # Keep terminal output and send the message to the UI.
            print(Message)
            ResultQueue.put(("Status", Message))


        def ReportFileProgress(ConvertedCount, TotalFiles):
            ResultQueue.put(("Progress", (ConvertedCount, TotalFiles)))

        def RunConversion():
            try:
                ConvertFolder(
                    Report=ReportStatus,
                    ReportProgress=ReportFileProgress,
                    **SelectedSettings
                )
            except Exception as Error:
                ResultQueue.put(("Error", str(Error)))
            else:
                ResultQueue.put(("Success", None))

        def CheckConversion():
            try:
                # Process all currently available messages.
                while True:
                    Result, Message = ResultQueue.get_nowait()

                    if Result == "Status":
                        self.StatusVariable.set(Message)

                    elif Result == "Progress":
                        ConvertedCount, TotalFiles = Message

                        self.FileCountVariable.set(
                            f"{ConvertedCount}/{TotalFiles} files converted"
                        )

                    elif Result == "Error":
                        self.ConvertButton.configure(state="normal")
                        self.StatusVariable.set("Conversion failed")
                        MessageBox.showerror(
                            "Conversion Error",
                            Message,
                            parent=self.Root
                        )
                        return

                    elif Result == "Success":
                        self.ConvertButton.configure(state="normal")

                        # Keep the converter's final summary visible.
                        return

            except Empty:
                self.Root.after(100, CheckConversion)

        Thread(target=RunConversion).start()
        self.Root.after(100, CheckConversion)

    def GetPreviewSourceSize(self):
        Directory = self.DirectoryVariable.get().strip()
        for FileName in GetFilesInDirectory(Directory):
            try:
                with Image.open(Os.path.join(Directory, FileName)) as Img:
                    return Img.size
            except (OSError, ValueError):
                continue
        return None

    def ToggleResizeControls(self):
        if self.ResizeEnabledVariable.get():
            self.ResizeFieldsFrame.pack(fill="x", pady=(10, 0))
            self.UpdateResizeDimensions()
        else:
            self.ResizeFieldsFrame.pack_forget()

    def OnRatioSelected(self):
        if self.RatioNameVariable.get() == "Custom":
            self.KeepAspectRatioVariable.set(False)
        else:
            self.KeepAspectRatioVariable.set(True)
        self.UpdateResizeDimensions()

    def OnDimensionChanged(self, ChangedField):
        if self._UpdatingDimensions:
            return
        self.LastDimensionChanged = ChangedField
        self.UpdateResizeDimensions()

    def UpdateResizeDimensions(self):
        if self._UpdatingDimensions or not self.ResizeEnabledVariable.get():
            return
        if not self.KeepAspectRatioVariable.get() or self.RatioNameVariable.get() == "Custom":
            self.ResizeHintVariable.set("Width and height can be edited independently.")
            return
        SourceSize = self.GetPreviewSourceSize() if self.RatioNameVariable.get() == "Original" else None
        if self.RatioNameVariable.get() == "Original" and SourceSize is None:
            self.ResizeHintVariable.set("Original ratio: using each source image during conversion. Add an input folder to preview dimensions.")
            return
        try:
            Width, Height = CalculateDimensions(
                self.ResizeWidthVariable.get(), self.ResizeHeightVariable.get(),
                RatioName=self.RatioNameVariable.get(), OriginalSize=SourceSize,
                ChangedField=self.LastDimensionChanged, KeepAspectRatio=True
            )
        except ValueError:
            return  # Permit partially typed values; validate when conversion starts.
        self._UpdatingDimensions = True
        try:
            if self.LastDimensionChanged == "width":
                self.ResizeHeightVariable.set(str(Height))
            else:
                self.ResizeWidthVariable.set(str(Width))
        finally:
            self._UpdatingDimensions = False
        self.ResizeHintVariable.set("Dimensions snap to whole pixels; selected aspect ratio stays locked.")

    def __init__(self):
        super().__init__()
        # Load saved values before creating the window.
        SavedSettings = LoadSettings()
        self.Colors = LoadColors(SavedSettings)

        # Use saved values when available; otherwise keep the defaults.
        Directory = SavedSettings.get("InputDirectory", globals()["Directory"])
        FinishedFolderName = SavedSettings.get("FinishedFolderName", globals()["FinishedFolderName"])
        OutputMode = SavedSettings.get("OutputMode", globals()["OutputMode"])
        ExistingOutputDirectory = SavedSettings.get(
            "ExistingOutputDirectory",
            globals()["ExistingOutputDirectory"]
        )
        # Fall back to the default if the saved selection is unrecognized.
        if OutputMode not in ("Create New Folder", "Save to Existing Folder"):
            OutputMode = "Create New Folder"
        MaxFileSize = SavedSettings.get("MaxFileSize", globals()["MaxFileSize"])
        DoMaxSizeCheck = SavedSettings.get("DoMaxSizeCheck", globals()["DoMaxSizeCheck"])
        StartQuality = SavedSettings.get("StartQuality", globals()["StartQuality"])
        MinimumQuality = SavedSettings.get("MinimumQuality", globals()["MinimumQuality"])
        QualityDecrement = SavedSettings.get("QualityDecrement", globals()["QualityDecrement"])
        CompressionMethod = SavedSettings.get("CompressionMethod", globals()["CompressionMethod"])
        FileNameAdditionStart = SavedSettings.get("FileNameAdditionStart", globals()["FileNameAdditionStart"])
        FileNameAdditionEnd = SavedSettings.get("FileNameAdditionEnd", globals()["FileNameAdditionEnd"])

        BackgroundColor = self.Colors["BackgroundColor"]
        TextColor = self.Colors["TextColor"]
        InputColor = self.Colors["InputColor"]
        BorderColor = self.Colors["BorderColor"]
        ButtonColor = self.Colors["ButtonColor"]
        ButtonHoverColor = self.Colors["ButtonHoverColor"]
        ButtonPressedColor = self.Colors["ButtonPressedColor"]
        ButtonTextColor = self.Colors["ButtonTextColor"]
        MutedTextColor = self.Colors["MutedTextColor"]

        # Create the main window.
        self.Root = self

        # Set the Windows title-bar icon.
        if Sys.platform == "win32":
            IconPath = Path(__file__).resolve().parent / "Icon.ico"
            if IconPath.is_file():
                try:
                    self.Root.iconbitmap(default=str(IconPath))
                except Tk.TclError:
                    pass


        self.Root.title("Folder2WebP Version " + VersionNumber)
        self.Root.geometry("800x960")
        self.Root.minsize(640, 480)
        self.Root.configure(fg_color=BackgroundColor)

        # Keep existing ttk widgets consistent while we convert them.
        LabelStyle = Ttk.Style(self.Root)
        LabelStyle.theme_use("clam")

        for StyleName in (
            "TFrame",
            "TLabelframe",
            "TLabel",
            "TLabelframe.Label",
            "TCheckbutton"
        ):
            LabelStyle.configure(
                StyleName,
                background=BackgroundColor
            )

        for StyleName in (
            "TLabel",
            "TLabelframe.Label",
            "TCheckbutton"
        ):
            LabelStyle.configure(
                StyleName,
                foreground=TextColor
            )

        LabelStyle.map(
            "TCheckbutton",
            background=[("active", BackgroundColor)],
            foreground=[("active", TextColor)]
        )
         # Style all text boxes, numeric boxes, and dropdowns.
        for StyleName in ("TEntry", "TSpinbox", "TCombobox"):
            LabelStyle.configure(
                StyleName,
                fieldbackground=InputColor,
                background=InputColor,
                foreground=TextColor,
                insertcolor=TextColor,
                arrowcolor=TextColor,
                bordercolor=BorderColor,
                lightcolor=BorderColor,
                darkcolor=BorderColor,
                padding=5
            )

            # Override theme colors for readonly and disabled fields.
            LabelStyle.map(
                StyleName,
                fieldbackground=[
                    ("disabled", InputColor),
                    ("readonly", InputColor)
                ],
                foreground=[
                    ("disabled", MutedTextColor),
                    ("!disabled", TextColor)
                ],
                background=[
                    ("active", BorderColor),
                    ("!active", InputColor)
                ],
                bordercolor=[
                    ("focus", ButtonColor)
                ]
            )
        # Keep readonly dropdown text from showing a contrasting highlight.
        LabelStyle.map(
            "TCombobox",
            selectbackground=[("readonly", InputColor)],
            selectforeground=[("readonly", TextColor)]
        )
        # Style both Browse and Convert Images.
        LabelStyle.configure(
            "TButton",
            background=ButtonColor,
            foreground="#FFFFFF",
            bordercolor=ButtonColor,
            lightcolor=ButtonColor,
            darkcolor=ButtonColor,
            padding=(12, 7),
            font=("Segoe UI", 10, "bold")
        )

        # First matching state wins: disabled, pressed, then hovered.
        LabelStyle.map(
            "TButton",
            background=[
                ("disabled", InputColor),
                ("pressed", ButtonPressedColor),
                ("active", ButtonHoverColor)
            ],
            foreground=[
                ("disabled", MutedTextColor),
                ("!disabled", "#FFFFFF")
            ]
        )

        # Style the list that opens from the compression dropdown.
        self.Root.option_add("*TCombobox*Listbox.background", InputColor)
        self.Root.option_add("*TCombobox*Listbox.foreground", TextColor)
        self.Root.option_add("*TCombobox*Listbox.selectBackground", ButtonColor)
        self.Root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")

        # Create and display the transparent main container.
        MainFrame = CTk.CTkScrollableFrame(
            self.Root,
            fg_color="transparent",
            corner_radius=0
        )
        MainFrame.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=24
        )

        # Create and display the title.
        TitleLabel = CTk.CTkLabel(
            MainFrame,
            text="Convert Images in a Folder to WebP",
            fg_color="transparent",
            text_color=TextColor,
            font=("Segoe UI", 28, "bold")
        )
        TitleLabel.pack(
            fill="x",
            pady=(0, 24)
        )

        # Hold the selected directory. Begin with your existing setting.
        self.DirectoryVariable = Tk.StringVar(value=Directory)
        self.DirectoryVariable.trace_add("write", lambda *Args: self.UpdateResizeDimensions() if hasattr(self, "ResizeEnabledVariable") else None)

        DirectoryLabel = Ttk.Label(MainFrame, text="Input Directory")
        DirectoryLabel.pack(anchor="w", pady=(0, 5))

        # Keep the text field and Browse button together.
        DirectoryFrame = Ttk.Frame(MainFrame)
        DirectoryFrame.pack(fill="x", pady=(0, 16))

        DirectoryEntry = Ttk.Entry(
            DirectoryFrame,
            textvariable=self.DirectoryVariable
        )
        DirectoryEntry.pack(side="left", fill="x", expand=True)

        BrowseButton = CTk.CTkButton(
            DirectoryFrame,
            text="Browse...",
            command=lambda: self.BrowseDirectory(self.Root, self.DirectoryVariable),
            width=110,
            height=34,
            corner_radius=8,
            fg_color=ButtonColor,
            hover_color=ButtonHoverColor,
            text_color="#FFFFFF",
            text_color_disabled=MutedTextColor,
            font=("Segoe UI", 13, "bold")
        )
        BrowseButton.pack(side="left", padx=(8, 0))

        # Output choice and remembered field values.
        self.OutputModeVariable = Tk.StringVar(value=OutputMode)
        self.FinishedFolderNameVariable = Tk.StringVar(value=FinishedFolderName)
        self.ExistingOutputDirectoryVariable = Tk.StringVar(
            value=ExistingOutputDirectory
        )

        # Keep both conditional frames inside one fixed section.
        OutputSection = Ttk.Frame(MainFrame)
        OutputSection.pack(fill="x", pady=(0, 16))

        OutputModeLabel = Ttk.Label(
            OutputSection,
            text="Save Converted Images"
        )
        OutputModeLabel.pack(anchor="w", pady=(0, 5))

        OutputModeEntry = Ttk.Combobox(
            OutputSection,
            textvariable=self.OutputModeVariable,
            values=("Create New Folder", "Save to Existing Folder"),
            state="readonly"
        )
        OutputModeEntry.pack(fill="x")

        # Controls for creating a folder beside the input folder.
        self.NewFolderFrame = Ttk.Frame(OutputSection)

        FinishedFolderNameLabel = Ttk.Label(
            self.NewFolderFrame,
            text="Finished Folder Name"
        )
        FinishedFolderNameLabel.pack(anchor="w", pady=(0, 5))

        FinishedFolderNameEntry = Ttk.Entry(
            self.NewFolderFrame,
            textvariable=self.FinishedFolderNameVariable
        )
        FinishedFolderNameEntry.pack(fill="x")

        # Controls for choosing an existing output folder.
        self.ExistingFolderFrame = Ttk.Frame(OutputSection)

        ExistingOutputDirectoryLabel = Ttk.Label(
            self.ExistingFolderFrame,
            text="Save to Existing Folder"
        )
        ExistingOutputDirectoryLabel.pack(anchor="w", pady=(0, 5))

        ExistingOutputDirectoryRow = Ttk.Frame(self.ExistingFolderFrame)
        ExistingOutputDirectoryRow.pack(fill="x")

        ExistingOutputDirectoryEntry = Ttk.Entry(
            ExistingOutputDirectoryRow,
            textvariable=self.ExistingOutputDirectoryVariable
        )
        ExistingOutputDirectoryEntry.pack(
            side="left",
            fill="x",
            expand=True
        )

        OutputBrowseButton = CTk.CTkButton(
            ExistingOutputDirectoryRow,
            text="Browse...",
            command=lambda: self.BrowseDirectory(
                self.Root,
                self.ExistingOutputDirectoryVariable,
                "Select the folder for converted images"
            ),
            width=110,
            height=34,
            corner_radius=8,
            fg_color=ButtonColor,
            hover_color=ButtonHoverColor,
            text_color=ButtonTextColor,
            text_color_disabled=MutedTextColor,
            font=("Segoe UI", 13, "bold")
        )
        OutputBrowseButton.pack(side="left", padx=(8, 0))

        # Update the visible fields whenever the selection changes.
        OutputModeEntry.bind(
            "<<ComboboxSelected>>",
            lambda Event: self.ToggleOutputControls(
                self.OutputModeVariable,
                self.NewFolderFrame,
                self.ExistingFolderFrame
            )
        )

        # Apply the remembered selection when the window opens.
        self.ToggleOutputControls(
            self.OutputModeVariable,
            self.NewFolderFrame,
            self.ExistingFolderFrame
        )

        self.StartQualityVariable = Tk.StringVar(value=str(StartQuality))

        StartQualityLabel = Ttk.Label(
            MainFrame,
            text="Start Quality (0–100)"
        )
        StartQualityLabel.pack(anchor="w", pady=(0, 5))

        StartQualityEntry = Ttk.Spinbox(
            MainFrame,
            from_=0,
            to=100,
            increment=1,
            textvariable=self.StartQualityVariable,
            width=10
        )
        StartQualityEntry.pack(anchor="w", pady=(0, 16))

            # --------------------------------------------------
        # Maximum-size settings
        # --------------------------------------------------
        self.DoMaxSizeCheckVariable = Tk.BooleanVar(value=DoMaxSizeCheck)
        self.MaxFileSizeVariable = Tk.StringVar(value=str(MaxFileSize))
        self.MinimumQualityVariable = Tk.StringVar(value=str(MinimumQuality))
        self.QualityDecrementVariable = Tk.StringVar(value=str(QualityDecrement))

        SizeSection = Ttk.LabelFrame(
            MainFrame,
            text="File Size Limit",
            padding=10
        )
        SizeSection.pack(fill="x", pady=(0, 16))

        # This frame holds the three conditional fields.
        self.SizeFieldsFrame = Ttk.Frame(SizeSection)

        SizeCheckButton = Ttk.Checkbutton(
            SizeSection,
            text="Enforce maximum file size",
            variable=self.DoMaxSizeCheckVariable,
            command=lambda: self.ToggleSizeControls(
                self.DoMaxSizeCheckVariable,
                self.SizeFieldsFrame
            )
        )
        SizeCheckButton.pack(anchor="w")

        self.SizeFieldsFrame.columnconfigure(0, weight=1)
        self.SizeFieldsFrame.columnconfigure(1, weight=1)
        self.SizeFieldsFrame.columnconfigure(2, weight=1)

        MaxFileSizeLabel = Ttk.Label(
            self.SizeFieldsFrame,
            text="Maximum File Size (KB)"
        )
        MaxFileSizeLabel.grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 5)
        )

        MaxFileSizeEntry = Ttk.Entry(
            self.SizeFieldsFrame,
            textvariable=self.MaxFileSizeVariable,
            width=12
        )
        MaxFileSizeEntry.grid(
            row=1, column=0, sticky="ew", padx=(0, 12)
        )

        MinimumQualityLabel = Ttk.Label(
            self.SizeFieldsFrame,
            text="Minimum Quality"
        )
        MinimumQualityLabel.grid(
            row=0, column=1, sticky="w", padx=(0, 12), pady=(0, 5)
        )

        MinimumQualityEntry = Ttk.Spinbox(
            self.SizeFieldsFrame,
            from_=0,
            to=100,
            increment=1,
            textvariable=self.MinimumQualityVariable,
            width=12
        )
        MinimumQualityEntry.grid(
            row=1, column=1, sticky="ew", padx=(0, 12)
        )

        QualityDecrementLabel = Ttk.Label(
            self.SizeFieldsFrame,
            text="Quality Decrement"
        )
        QualityDecrementLabel.grid(
            row=0, column=2, sticky="w", pady=(0, 5)
        )

        QualityDecrementEntry = Ttk.Spinbox(
            self.SizeFieldsFrame,
            from_=1,
            to=100,
            increment=1,
            textvariable=self.QualityDecrementVariable,
            width=12
        )
        QualityDecrementEntry.grid(
            row=1, column=2, sticky="ew"
        )

        # Apply the checkbox's initial state.
        self.ToggleSizeControls(self.DoMaxSizeCheckVariable, self.SizeFieldsFrame)

        # --------------------------------------------------
        # Compression method
        # --------------------------------------------------
        self.CompressionMethodVariable = Tk.StringVar(
            value=str(CompressionMethod)
        )

        CompressionMethodLabel = Ttk.Label(
            MainFrame,
            text="Compression Method"
        )
        CompressionMethodLabel.pack(anchor="w", pady=(0, 5))

        CompressionMethodEntry = Ttk.Combobox(
            MainFrame,
            textvariable=self.CompressionMethodVariable,
            values=tuple(range(7)),
            state="readonly",
            width=10
        )
        CompressionMethodEntry.pack(anchor="w")

        CompressionMethodHint = Ttk.Label(
            MainFrame,
            text="0 = fastest encoding; 6 = slower, more compression effort"
        )
        CompressionMethodHint.pack(anchor="w", pady=(5, 16))

        # --------------------------------------------------
        # Filename additions
        # --------------------------------------------------
        self.FileNameAdditionStartVariable = Tk.StringVar(
            value=FileNameAdditionStart
        )
        self.FileNameAdditionEndVariable = Tk.StringVar(
            value=FileNameAdditionEnd
        )

        FileNameFrame = Ttk.Frame(MainFrame)
        FileNameFrame.pack(fill="x", pady=(0, 16))

        FileNameFrame.columnconfigure(0, weight=1)
        FileNameFrame.columnconfigure(1, weight=1)

        FileNameAdditionStartLabel = Ttk.Label(
            FileNameFrame,
            text="Filename Addition Start"
        )
        FileNameAdditionStartLabel.grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 5)
        )

        FileNameAdditionStartEntry = Ttk.Entry(
            FileNameFrame,
            textvariable=self.FileNameAdditionStartVariable
        )
        FileNameAdditionStartEntry.grid(
            row=1, column=0, sticky="ew", padx=(0, 12)
        )

        FileNameAdditionEndLabel = Ttk.Label(
            FileNameFrame,
            text="Filename Addition End"
        )
        FileNameAdditionEndLabel.grid(
            row=0, column=1, sticky="w", pady=(0, 5)
        )

        FileNameAdditionEndEntry = Ttk.Entry(
            FileNameFrame,
            textvariable=self.FileNameAdditionEndVariable
        )
        FileNameAdditionEndEntry.grid(
            row=1, column=1, sticky="ew"
        )

        # Optional image resizing controls.
        self.ResizeEnabledVariable = Tk.BooleanVar(value=SavedSettings.get("ResizeEnabled", False))
        self.KeepAspectRatioVariable = Tk.BooleanVar(value=SavedSettings.get("KeepAspectRatio", True))
        SavedRatio = SavedSettings.get("RatioName", "Original")
        self.RatioNameVariable = Tk.StringVar(value=SavedRatio if SavedRatio in ASPECT_RATIOS else "Original")
        self.ResizeWidthVariable = Tk.StringVar(value=str(SavedSettings.get("ResizeWidth", "1200")))
        self.ResizeHeightVariable = Tk.StringVar(value=str(SavedSettings.get("ResizeHeight", "800")))
        self.LastDimensionChanged = SavedSettings.get("ChangedField", "width")
        self._UpdatingDimensions = False

        ResizeSection = Ttk.LabelFrame(MainFrame, text="Image Resizing", padding=10)
        ResizeSection.pack(fill="x", pady=(0, 16))
        Ttk.Checkbutton(ResizeSection, text="Resize Images", variable=self.ResizeEnabledVariable,
                        command=self.ToggleResizeControls).pack(anchor="w")
        self.ResizeFieldsFrame = Ttk.Frame(ResizeSection)
        Ttk.Checkbutton(self.ResizeFieldsFrame, text="Keep Aspect Ratio",
                        variable=self.KeepAspectRatioVariable,
                        command=self.UpdateResizeDimensions).pack(anchor="w", pady=(0, 8))
        Ttk.Label(self.ResizeFieldsFrame, text="Common Aspect Ratios").pack(anchor="w")
        self.RatioEntry = Ttk.Combobox(self.ResizeFieldsFrame, textvariable=self.RatioNameVariable,
                                       values=list(ASPECT_RATIOS), state="readonly")
        self.RatioEntry.pack(fill="x", pady=(4, 8))
        self.RatioEntry.bind("<<ComboboxSelected>>", lambda Event: self.OnRatioSelected())
        # Distortion/cropping behavior for images whose shape differs from the target.
        SavedMethod = SavedSettings.get("ResizeMethod", "Stretch / Squash")
        self.ResizeMethodVariable = Tk.StringVar(
            value=SavedMethod if SavedMethod in RESIZE_METHODS else "Stretch / Squash"
        )
        Ttk.Label(self.ResizeFieldsFrame, text="Resize Method").pack(anchor="w")
        Ttk.Combobox(
            self.ResizeFieldsFrame,
            textvariable=self.ResizeMethodVariable,
            values=list(RESIZE_METHODS),
            state="readonly"
        ).pack(fill="x", pady=(4, 8))
        ResizeRow = Ttk.Frame(self.ResizeFieldsFrame)
        ResizeRow.pack(fill="x")
        for Index, (LabelText, Variable, Field) in enumerate((
            ("Width (px)", self.ResizeWidthVariable, "width"),
            ("Height (px)", self.ResizeHeightVariable, "height"),
        )):
            ResizeRow.columnconfigure(Index, weight=1)
            Column = Ttk.Frame(ResizeRow)
            Column.grid(row=0, column=Index, sticky="ew", padx=(0, 12) if Index == 0 else 0)
            Ttk.Label(Column, text=LabelText).pack(anchor="w")
            Ttk.Entry(Column, textvariable=Variable).pack(fill="x", pady=(4, 0))
            Variable.trace_add("write", lambda *Args, Changed=Field: self.OnDimensionChanged(Changed))
        self.ResizeHintVariable = Tk.StringVar(value="")
        Ttk.Label(self.ResizeFieldsFrame, textvariable=self.ResizeHintVariable,
                  wraplength=560).pack(anchor="w", pady=(6, 0))
        self.ToggleResizeControls()

        self.ConvertButton = CTk.CTkButton(
            MainFrame,
            text="Convert Images",
            command=self.StartConversion,
            width=200,
            height=42,
            corner_radius=8,
            fg_color=ButtonColor,
            hover_color=ButtonHoverColor,
            text_color="#FFFFFF",
            text_color_disabled=MutedTextColor,
            font=("Segoe UI", 14, "bold")
        )
        self.ConvertButton.pack(pady=(12, 0))

        self.StatusVariable = Tk.StringVar(value="Ready to Convert")

        StatusLabel = Ttk.Label(
            MainFrame,
            textvariable=self.StatusVariable,
            font=("Segoe UI", 9)
        )
        StatusLabel.configure(anchor="center", justify="center")
        StatusLabel.pack(fill="x", pady=(8, 0))
        self.FileCountVariable = Tk.StringVar(value="0/0 files converted")

        FileCountLabel = Ttk.Label(
            MainFrame,
            textvariable=self.FileCountVariable,
            font=("Segoe UI", 9)
        )
        FileCountLabel.configure(anchor="center", justify="center")
        FileCountLabel.pack(fill="x", pady=(4, 0))

        #The Following Items Go from the bottom up!

        CreditLabel = Ttk.Label(
            MainFrame,
            text="Created By Nathan Taylor. Version "+VersionNumber,
            font=("Segoe UI", 9)
        )
        CreditLabel.configure(anchor="center", justify="center")
        CreditLabel.pack(side="bottom", fill="x", pady=(4, 0))

        # Save current fields when the window's X button is clicked.
        self.Root.protocol("WM_DELETE_WINDOW", self.CloseWindow)

