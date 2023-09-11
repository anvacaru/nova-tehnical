from __future__ import annotations

from enum import Enum
from pathlib import Path
from tkinter.filedialog import askdirectory
from typing import TYPE_CHECKING, Optional

import psutil
from psutil import Process

if TYPE_CHECKING:
    pass


def get_process(process_name: str) -> Optional[Process]:
    for process in psutil.process_iter():
        try:
            if process_name.lower() in process.name().lower():
                return process
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None


def check_file_path(path: Path) -> None:
    path = path.resolve()
    if not path.exists():
        raise ValueError(f'File does not exist: {path}')
    if not path.is_file():
        raise ValueError(f'Path is not a file: {path}')


def check_dir_path(path: Path) -> None:
    path = path.resolve()
    if not path.exists():
        raise ValueError(f'Directory does not exist: {path}')
    if not path.is_dir():
        raise ValueError(f'Path is not a directory: {path}')


def get_input_path() -> Path:
    return Path(f'{askdirectory(title="Visitor photos and voice recordings", mustexist=True)}')


class OSName(Enum):
    WINDOWS = 'Windows'
    DARWIN = 'Darwin'
    LINUX = 'Linux'
