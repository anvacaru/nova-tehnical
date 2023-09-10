from __future__ import annotations

import logging
import os
import platform
import subprocess
from os import scandir
from pathlib import Path
from typing import Final

from ..utils import check_dir_path
from .processing import (
    LOWER_BOUND_2,
    UPPER_BOUND_2,
    heic_to_jpg,
    process_image_with_opencv_bounds,
    process_image_with_opencv_dominant,
    process_image_with_opencv_treshold,
    process_image_with_pillow,
    process_video_with_opencv_bounds,
    process_video_with_opencv_dominant_color,
)

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

    def run_all_photos(self, output_dir: Path) -> None:
        for p in self.photos:
            process_image_with_pillow(image_path=p, output_path=Path(os.path.join(output_dir, (p.stem + 'pillow.png'))))
            process_image_with_opencv_treshold(
                image_path=p, output_path=Path(os.path.join(output_dir, (p.stem + 'treshold.png')))
            )
            process_image_with_opencv_dominant(
                image_path=p, output_path=Path(os.path.join(output_dir, (p.stem + 'dominant.png')))
            )
            process_image_with_opencv_bounds(
                image_path=p,
                output_path=Path(os.path.join(output_dir, (p.stem + 'bounds.png'))),
                lbound=LOWER_BOUND_2,
                ubound=UPPER_BOUND_2,
            )

    def process_heic_files(self) -> None:
        for p in self.heic_photos:
            np = heic_to_jpg(p)
            self._files.append(np)

    def process_video_files(self, output_dir: Path) -> None:
        for p in self.videos:
            process_video_with_opencv_bounds(
                input_path=str(p), output_path=os.path.join(output_dir, (p.stem + 'bounds.mov'))
            )
            process_video_with_opencv_bounds(
                input_path=str(p),
                output_path=os.path.join(output_dir, (p.stem + 'bounds_frames')),
                export_to_frames=True,
            )
            process_video_with_opencv_dominant_color(
                input_path=str(p), output_path=os.path.join(output_dir, (p.stem + 'dominant.mov'))
            )
            process_video_with_opencv_dominant_color(
                input_path=str(p),
                output_path=os.path.join(output_dir, (p.stem + 'dominant_frames')),
                export_to_frames=True,
            )
            self.invoke_ffmpeg(
                input_path=Path(os.path.join(output_dir, (p.stem + 'bounds_frames'))),
                output_path=Path(os.path.join(output_dir, (p.stem + 'bounds_frames.mov'))),
            )
            self.invoke_ffmpeg(
                input_path=Path(os.path.join(output_dir, (p.stem + 'dominant_frames'))),
                output_path=Path(os.path.join(output_dir, (p.stem + 'dominant_frames.mov'))),
            )
