from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from typing import TYPE_CHECKING, Final, NoReturn, Type

import psutil
from psutil import Process

if TYPE_CHECKING:
    pass

_LOGGER: Final = logging.getLogger(__name__)


def get_process(process_name: str) -> Process | None:
    for process in psutil.process_iter():
        try:
            if process_name.lower() in process.name().lower():
                return process
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None


def get_files_by_extension(input_dir: Path, accepted_extensions: list[str]) -> list[Path]:
    _LOGGER.info(f'Reading {accepted_extensions} files from {input_dir}.')
    files = sorted(
        [file_path for file_path in input_dir.iterdir() if file_path.suffix.lower() in accepted_extensions],
        key=lambda x: x.name,
    )
    _LOGGER.debug(f'Found {len(files)} files: {files}.')
    return files


def check_file_path(path: Path) -> None:
    path = path.resolve()
    if not path.exists():
        raise_error(error_class=ValueError, message=f'File does not exist: {path}')
    if not path.is_file():
        raise_error(error_class=ValueError, message=f'Path is not a file: {path}')


def check_dir_path(path: Path) -> None:
    path = path.resolve()
    if not path.exists():
        raise_error(error_class=ValueError, message=f'Directory does not exist: {path}')
    if not path.is_dir():
        raise_error(error_class=ValueError, message=f'Path is not a directory: {path}')


def get_input_path() -> Path:
    return Path(f'{askdirectory(title="Visitor photos and voice recordings", mustexist=True)}')


def raise_error(error_class: Type[Exception], message: str) -> NoReturn:
    showerror(title='Error', message=message)
    raise error_class(message)


class OSName(Enum):
    WINDOWS = 'Windows'
    DARWIN = 'Darwin'
    LINUX = 'Linux'
