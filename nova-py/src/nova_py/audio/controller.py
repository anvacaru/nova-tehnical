from __future__ import annotations

import logging
import platform
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Final, List

from ..utils import OSName, check_dir_path, get_files_by_extension, get_process, raise_error
from .pipeclient import PipeClient

if TYPE_CHECKING:
    pass

_LOGGER: Final = logging.getLogger(__name__)
AUDACITY_WAIT_TIME: Final = 3


class AudacityController:
    def __init__(self) -> None:
        os_name = platform.system()
        _LOGGER.info(f'Operating system name: {os_name}')

        self._total_tracks: int = 0
        self._EOL: str
        self._CMD: List[str]
        self._process_name: str
        self._client: PipeClient
        if os_name == OSName.WINDOWS.value:
            self._process_name = 'C:\\Program Files\\Audacity\\Audacity.exe'
            self._CMD = [self._process_name]
        elif os_name in {OSName.DARWIN.value, OSName.LINUX.value}:
            self._process_name = 'audacity'
            self._CMD = [self._process_name] if os_name == OSName.LINUX.value else ['open', '-a', 'Audacity']
        else:
            raise_error(error_class=EnvironmentError, message=f'Unsupported operating system: {os_name}')

    def save_project(self, output_path: str, add_to_history: bool = False, compress: bool = False) -> None:
        self.do_command(
            command=f'SaveProject2: Filename={output_path} AddToHistory={add_to_history} Compress={compress}'
        )

    def import_audio(self, input_path: Path) -> int:
        p = str(input_path).replace('\\', '/')
        self.do_command(command=f'Import2: Filename="{p}"')
        self._total_tracks += 1
        return self._total_tracks - 1

    def import_audio_batch(self, input_dir: Path) -> None:
        check_dir_path(input_dir)
        wav_files = get_files_by_extension(input_dir=input_dir, accepted_extensions=['.m4a', '.mp3'])
        for file_path in wav_files:
            self.import_audio(input_path=file_path)

    def move_audio_clip(self, track: int, destinations: list[int], duration: int) -> None:
        self.select_audio(track=track, start=0, end=0)
        self.select_cursor_to_next_clip_boundary()
        self.cut_audio()
        for start in destinations:
            self.select_audio(track=track, start=start, end=start + duration)
            self.paste_audio()

    def select_audio(self, track: int = 0, start: int = 0, end: int = 0) -> None:
        if track < 0 or track >= self._total_tracks:
            raise_error(error_class=ValueError, message=f'Invalid track number: {track}')
        self.do_command(command=f'Select: Start={start} End={end} Track={track}')

    def select_cursor_to_next_clip_boundary(self) -> None:
        self.do_command(command='SelCursorToNextClipBoundary')

    def select_all(self) -> None:
        self.do_command(command='SelectAll')

    def select_tracks(self, track: int, count: int = 1) -> None:
        self.do_command(command=f'SelectTracks: Mode=Set Track={track} TrackCount={count}')

    def add_delay(self) -> None:
        self.do_command(command='Delay: delay=0.5, number=4')

    def select(self, start: int, end: int, track: int, count: int) -> None:
        self.do_command(command=f'Select: Start={start} End={end}, Track={track}, TrackCount={count}')

    def remove_tracks(self) -> None:
        self.do_command(command='RemoveTracks')

    def echo_audio(self) -> None:
        self.do_command(command='Echo: Delay=3')

    def cut_audio(self) -> None:
        self.do_command(command='Cut')

    def paste_audio(self) -> None:
        self.do_command(command='Paste')

    def delete_audio(self) -> None:
        self.do_command(command='Delete')

    def export_audio(self) -> None:
        export_command = 'Export2: Filename="D:/NOVA/Have you seen my body/voices.aiff"'
        self.do_command(command=export_command)
        time.sleep(5)

    def add_reverb_vocal1(self) -> None:
        reverb_command = 'Reverb: RoomSize:70, Delay=20, Reverberance=40, HfDamping=99, ToneLow=100, ToneHigh=50, WetGain=-12, DryGain=0, StereoWidth=70'
        self.do_command(command=reverb_command)

    def add_reverb_largeroom(self) -> None:
        reverb_command = 'Reverb: RoomSize:85, Delay=10, Reverberance=40, HfDamping=50, ToneLow=100, ToneHigh=80, WetGain=0, DryGain=-6, StereoWidth=90'
        self.do_command(command=reverb_command)

    def stop_audacity(self) -> None:
        self._client.write(command='Exit')

    def do_command(self, command: str) -> str:
        _LOGGER.debug(f'Sending command to Audacity: {command}')
        self._client.write(command=command, timer=True)
        response = self._client.read()
        _LOGGER.debug(f'Received response from Audacity: {response}')
        time.sleep(0.4)
        return response

    def start_audacity(self) -> int:
        _LOGGER.info('Checking if Audacity is running.')
        process = get_process(process_name=self._process_name)
        if process:
            _LOGGER.info(f'Audacity is already running with pid: {process.pid}')
            self._client = PipeClient()
            return process.pid

        _LOGGER.info('Launching Audacity process...')
        try:
            new_process = subprocess.Popen(self._CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            time.sleep(2)
            self._client = PipeClient()
        except Exception:
            raise_error(error_class=RuntimeError, message='Failed to start Audacity process.')

        _LOGGER.debug(f'Audacity process started successfully with pid: {new_process.pid}')
        time.sleep(AUDACITY_WAIT_TIME)

        return new_process.pid
