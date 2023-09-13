from __future__ import annotations

import logging
import os
import platform
from pathlib import Path
from typing import Final

from PIL import Image  # type: ignore
from pillow_heif import register_heif_opener  # type: ignore

from ..utils import check_dir_path, get_files_by_extension

_LOGGER: Final = logging.getLogger(__name__)


class VisualController:
    IMG_EXTENSIONS: Final[list[str]] = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic']

    def __init__(self) -> None:
        os_name = platform.system()
        _LOGGER.info(f'Operating system name: {os_name}')

    def read_files(self, input_dir: Path, expected: int) -> None:
        check_dir_path(input_dir)
        self._files = get_files_by_extension(input_dir=input_dir, accepted_extensions=self.IMG_EXTENSIONS)
        if len(self._files) != expected:
            raise ValueError('Invalid Number of files!')

    def process_files(self, img_names: list[str], output_dir: Path) -> None:
        for i, file in enumerate(self._files):
            output_path = output_dir / img_names[i]
            self.convert_file(image_path=file, output_path=output_path)

    @staticmethod
    def is_photo(file_path: Path) -> bool:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic']
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
    def convert_file(image_path: Path, output_path: Path) -> None:
        _LOGGER.info(f'Converting {image_path} to {output_path}.')
        register_heif_opener()
        image = Image.open(image_path)
        image.convert('RGBA').save(output_path)
