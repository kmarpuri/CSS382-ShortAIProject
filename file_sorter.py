from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable


def unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def sort_files(
    target_directory: Path,
    dry_run: bool = False,
    reporter: Callable[[str], None] | None = None,
) -> int:
    moved_files = 0
    script_name = Path(__file__).name

    def emit(message: str) -> None:
        if reporter is None:
            print(message)
        else:
            reporter(message)

    for item in target_directory.iterdir():
        if not item.is_file() or item.name == script_name:
            continue

        extension = item.suffix.lower().lstrip(".") or "no_extension"
        destination_directory = target_directory / extension
        destination_file = unique_destination(destination_directory / item.name)

        if dry_run:
            emit(f"Would move {item.name} -> {destination_file.relative_to(target_directory)}")
            moved_files += 1
            continue

        destination_directory.mkdir(exist_ok=True)
        shutil.move(str(item), str(destination_file))
        emit(f"Moved {item.name} -> {destination_file.relative_to(target_directory)}")
        moved_files += 1

    return moved_files


def undo_files(
    target_directory: Path,
    dry_run: bool = False,
    reporter: Callable[[str], None] | None = None,
) -> int:
    restored_files = 0

    def emit(message: str) -> None:
        if reporter is None:
            print(message)
        else:
            reporter(message)

    for folder in sorted(target_directory.iterdir(), key=lambda path: path.name.lower()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue

        expected_extension = folder.name.lower()
        candidate_files = [item for item in folder.iterdir() if item.is_file()]
        if not candidate_files:
            continue

        matches_extension = all(
            (
                expected_extension == "no_extension" and item.suffix == ""
            )
            or item.suffix.lower().lstrip(".") == expected_extension
            for item in candidate_files
        )
        if not matches_extension:
            continue

        moved_any_file = False
        for item in candidate_files:

            destination_file = unique_destination(target_directory / item.name)
            if dry_run:
                emit(f"Would move {folder.name}/{item.name} -> {destination_file.name}")
            else:
                shutil.move(str(item), str(destination_file))
                emit(f"Moved {folder.name}/{item.name} -> {destination_file.name}")

            restored_files += 1
            moved_any_file = True

        if moved_any_file and not dry_run:
            try:
                folder.rmdir()
                emit(f"Removed folder {folder.name}")
            except OSError:
                emit(f"Kept folder {folder.name} because it is not empty")

    return restored_files


@dataclass
class SortResult:
    moved_files: int
    message: str


@dataclass
class UndoResult:
    restored_files: int
    message: str


def build_sort_result(
    target_directory: Path,
    dry_run: bool = False,
    reporter: Callable[[str], None] | None = None,
) -> SortResult:
    moved_files = sort_files(target_directory, dry_run=dry_run, reporter=reporter)
    if moved_files == 0:
        return SortResult(moved_files=0, message="No files to sort.")

    action = "would be sorted" if dry_run else "sorted"
    return SortResult(
        moved_files=moved_files,
        message=f"{moved_files} file(s) {action} in {target_directory}",
    )


def build_undo_result(
    target_directory: Path,
    dry_run: bool = False,
    reporter: Callable[[str], None] | None = None,
) -> UndoResult:
    restored_files = undo_files(target_directory, dry_run=dry_run, reporter=reporter)
    if restored_files == 0:
        return UndoResult(restored_files=0, message="No extension folders to undo.")

    action = "would be restored" if dry_run else "restored"
    return UndoResult(
        restored_files=restored_files,
        message=f"{restored_files} file(s) {action} in {target_directory}",
    )


def run_gui() -> None:
    root = tk.Tk()
    root.title("File Sorter")
    root.geometry("720x460")
    root.minsize(640, 400)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)

    title_frame = ttk.Frame(root, padding=(18, 16, 18, 8))
    title_frame.grid(row=0, column=0, sticky="ew")
    title_frame.columnconfigure(0, weight=1)

    ttk.Label(title_frame, text="File Sorter", font=("Helvetica", 18, "bold")).grid(
        row=0, column=0, sticky="w"
    )
    ttk.Label(
        title_frame,
        text="Choose a folder and sort files into folders by extension.",
    ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    controls = ttk.Frame(root, padding=(18, 8, 18, 8))
    controls.grid(row=1, column=0, sticky="ew")
    controls.columnconfigure(1, weight=1)

    directory_var = tk.StringVar(value=str(Path.cwd()))
    dry_run_var = tk.BooleanVar(value=False)
    status_var = tk.StringVar(value="Ready to sort.")
    mode_var = tk.StringVar(value="sort")

    def browse_for_folder() -> None:
        selected_directory = filedialog.askdirectory(initialdir=directory_var.get() or str(Path.cwd()))
        if selected_directory:
            directory_var.set(selected_directory)
            status_var.set("Folder selected.")

    def append_log(text_widget: tk.Text, message: str) -> None:
        text_widget.configure(state="normal")
        text_widget.insert("end", message + "\n")
        text_widget.see("end")
        text_widget.configure(state="disabled")

    ttk.Label(controls, text="Folder").grid(row=0, column=0, sticky="w", padx=(0, 10))
    directory_entry = ttk.Entry(controls, textvariable=directory_var)
    directory_entry.grid(row=0, column=1, sticky="ew")
    ttk.Button(controls, text="Browse", command=browse_for_folder).grid(
        row=0, column=2, sticky="e", padx=(10, 0)
    )

    ttk.Checkbutton(controls, text="Dry run", variable=dry_run_var).grid(
        row=1, column=1, sticky="w", pady=(12, 0)
    )

    mode_frame = ttk.Frame(controls)
    mode_frame.grid(row=2, column=1, sticky="w", pady=(12, 0))
    ttk.Radiobutton(mode_frame, text="Sort", variable=mode_var, value="sort").grid(
        row=0, column=0, sticky="w"
    )
    ttk.Radiobutton(mode_frame, text="Undo", variable=mode_var, value="undo").grid(
        row=0, column=1, sticky="w", padx=(12, 0)
    )

    action_row = ttk.Frame(root, padding=(18, 4, 18, 8))
    action_row.grid(row=2, column=0, sticky="nsew")
    action_row.columnconfigure(0, weight=1)
    action_row.rowconfigure(1, weight=1)

    log_box = tk.Text(action_row, wrap="word", height=10, state="disabled")
    log_box.grid(row=1, column=0, sticky="nsew")

    log_scroll = ttk.Scrollbar(action_row, orient="vertical", command=log_box.yview)
    log_scroll.grid(row=1, column=1, sticky="ns")
    log_box.configure(yscrollcommand=log_scroll.set)

    footer = ttk.Frame(root, padding=(18, 0, 18, 16))
    footer.grid(row=3, column=0, sticky="ew")
    footer.columnconfigure(0, weight=1)

    status_label = ttk.Label(footer, textvariable=status_var)
    status_label.grid(row=0, column=0, sticky="w")

    def run_sort() -> None:
        directory_value = Path(directory_var.get()).expanduser()
        if not directory_value.exists():
            messagebox.showerror("File Sorter", f"{directory_value} does not exist.")
            return

        if not directory_value.is_dir():
            messagebox.showerror("File Sorter", f"{directory_value} is not a directory.")
            return

        append_log(log_box, f"Folder: {directory_value}")
        append_log(log_box, f"Dry run: {dry_run_var.get()}")

        reporter = lambda message: append_log(log_box, message)
        if mode_var.get() == "undo":
            append_log(log_box, "Mode: undo")
            result = build_undo_result(
                directory_value.resolve(),
                dry_run=dry_run_var.get(),
                reporter=reporter,
            )
        else:
            append_log(log_box, "Mode: sort")
            result = build_sort_result(
                directory_value.resolve(),
                dry_run=dry_run_var.get(),
                reporter=reporter,
            )

        append_log(log_box, result.message)
        status_var.set(result.message)
        messagebox.showinfo("File Sorter", result.message)

    ttk.Button(footer, text="Run", command=run_sort).grid(row=0, column=1, sticky="e")

    append_log(log_box, "Select a folder and click Sort Files.")
    append_log(log_box, "Use Undo mode to restore files from extension folders.")
    root.mainloop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sort files into folders based on their extension."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=None,
        help="Folder to sort. If omitted, the GUI opens instead.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without moving files.",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Restore files from extension folders back into the chosen folder.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Open the graphical interface.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.gui or (args.directory is None and not args.dry_run and not args.undo):
        run_gui()
        return 0

    target_directory = Path(args.directory or ".").expanduser().resolve()

    if not target_directory.exists():
        print(f"Error: {target_directory} does not exist.")
        return 1

    if not target_directory.is_dir():
        print(f"Error: {target_directory} is not a directory.")
        return 1

    if args.undo:
        result = build_undo_result(target_directory, dry_run=args.dry_run, reporter=print)
    else:
        result = build_sort_result(target_directory, dry_run=args.dry_run, reporter=print)
    print(result.message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())