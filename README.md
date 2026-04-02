# CSS382-ShortAIProject

Python file sorter that organizes files into folders based on their extension. It includes a simple desktop interface, a command-line mode, and an undo feature.

## Project Info

- UWNetID: kmarpuri
- Name: Krish Marpuri
- GitHub Repository: [ShortAIProject](https://github.com/kmarpuri/CSS382-ShortAIProject)

## What It Does

The script scans a folder, creates a folder for each file extension it finds, and moves matching files into those folders.
It can also undo that sort by moving files back out of the extension folders.

Examples:

- `photo.jpg` -> `jpg/photo.jpg`
- `notes.txt` -> `txt/notes.txt`
- `archive.tar.gz` -> `gz/archive.tar.gz`
- `LICENSE` -> `no_extension/LICENSE`

## Requirements

- Python 3.10 or newer

The project uses only the Python standard library, so no extra packages are needed.

The interface uses Tkinter, which is included with standard Python on macOS and most common Python installs.

## How To Run

### Open The Interface

Run this command to open the GUI:

```bash
python file_sorter.py
```

In the window, choose a folder, optionally turn on dry run, then click Sort Files.

### Use The Command Line

To sort a folder directly without opening the GUI:

```bash
python file_sorter.py /path/to/folder
```

To preview changes without moving files:

```bash
python file_sorter.py /path/to/folder --dry-run
```

To undo a previous sort and move files back into the chosen folder:

```bash
python file_sorter.py /path/to/folder --undo
```

## Optional Flags

- `--dry-run` shows what would happen without moving any files.
- `--gui` forces the interface to open.
- `--undo` restores files from extension folders back into the selected folder.

Example:

```bash
python file_sorter.py --gui
```

## Notes

- Existing folders are reused if they already match a file extension.
- If two files would end up with the same name, the script adds a number to keep both files.
- The sorter does not move folders, only files.
- If you run the script with no folder argument, the GUI opens by default.
- Undo works on the top-level extension folders that the sorter created.

## Idea

Create a file sorter that puts things in folders based on the extension.