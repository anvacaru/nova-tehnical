from __future__ import annotations

import logging
import os
import platform
import subprocess
from os import scandir
from pathlib import Path
from typing import Final

from PIL import Image  # type: ignore
from pillow_heif import register_heif_opener  # type: ignore

from ..utils import check_dir_path

_LOGGER: Final = logging.getLogger(__name__)


class Controller:
    def __init__(self) -> None:
        os_name = platform.system()
        _LOGGER.info(f'Operating system name: {os_name}')

    def read_files(self, folder_path: Path) -> None:
        check_dir_path(folder_path)
        with scandir(folder_path) as entries:
            self._files = [Path(entry.path) for entry in entries if entry.is_file()]

    @staticmethod
    def is_photo(file_path: Path) -> bool:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        ext = os.path.splitext(file_path)[1].lower()
        return ext in extensions

    @staticmethod
    def is_heic_photo(file_path: Path) -> bool:
        return os.path.splitext(file_path)[1].lower() == '.heic'

    @staticmethod
    def is_video(file_path: Path) -> bool:
        extensions = ['.mov', '.mp4']
        ext = os.path.splitext(file_path)[1].lower()
        return ext in extensions

    @staticmethod
    def invoke_ffmpeg(input_path: Path, output_path: Path) -> None:
        # ffmpeg -i photos/output/frame_%04d.png -vcodec png z.mov
        cmd = ['ffmpeg', '-i', f'{input_path}/frame_%04d.png', '-vcodec', 'png', f'{output_path}']
        _LOGGER.info(f'Calling: {cmd}')
        subprocess.run(cmd, check=True)

    @property
    def photos(self) -> list[Path]:
        return [file for file in self._files if self.is_photo(file)]

    @property
    def videos(self) -> list[Path]:
        return [file for file in self._files if self.is_video(file)]

    @property
    def heic_photos(self) -> list[Path]:
        return [file for file in self._files if self.is_heic_photo(file)]

    @staticmethod
    def heic_to_jpg(image_path: Path) -> Path:
        _LOGGER.info(f'Converting {image_path} to jpg.')
        register_heif_opener()
        image = Image.open(image_path)
        stem = image_path.stem
        new_filename = stem + '.png'
        new_path = image_path.parent / new_filename
        image.convert('RGB').save(new_path)
        return new_path

    def process_heic_files(self) -> None:
        for p in self.heic_photos:
            np = self.heic_to_jpg(p)
            self._files.append(np)
