from __future__ import annotations

import logging
import platform
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Final, List

from .pipeclient import PipeClient
from .utils import OSName, check_dir_path, check_file_path, get_process

if TYPE_CHECKING:
    pass


_LOGGER: Final = logging.getLogger(__name__)
AUDACITY_WAIT_TIME: Final = 3
AUDACITY_TIMEOUT_TIME: Final = 10


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
            # uid = os.getuid()  # type: ignore
            self._process_name = 'audacity'
            self._CMD = [self._process_name] if os_name == OSName.LINUX.value else ['open', '-a', 'Audacity']
        else:
            raise EnvironmentError(f'Unsupported operating system: {os_name}')

    def save_project(self, output_path: str, add_to_history: bool = False, compress: bool = False) -> None:
        self.do_command(
            command=f'SaveProject2: Filename={output_path} AddToHistory={add_to_history} Compress={compress}'
        )

    def import_audio(self, input_path: str) -> int:
        check_file_path(Path(input_path))
        self.do_command(command=f'Import2: Filename={input_path}')
        self._total_tracks += 1
        return self._total_tracks - 1

    def import_audio_batch(self, input_dir: str) -> None:
        input_dir_object = Path(input_dir)
        check_dir_path(input_dir_object)
        wav_files = [file_path for file_path in input_dir_object.iterdir() if file_path.suffix == '.wav']

        for file_path in wav_files:
            self.import_audio(input_path=str(file_path))

    def move_audio_clip(self, track: int, destination_start: int, destination_end: int) -> None:
        self.select_audio(track=track, start=0, end=0)
        self.select_cursor_to_next_clip_boundary()
        self.cut_audio()
        self.select_audio(track=track, start=destination_start, end=destination_end)
        self.paste_audio()

    def select_audio(self, track: int = 0, start: int = 0, end: int = 0) -> None:
        if track < 0 or track >= self._total_tracks:
            raise ValueError(f'Invalid track number: {track}')
        self.do_command(command=f'Select: Start={start} End={end} Track={track}')

    def select_cursor_to_next_clip_boundary(self) -> None:
        self.do_command(command='SelCursorToNextClipBoundary')

    def select_all(self) -> None:
        self.do_command(command='SelectAll')

    def select_tracks(self, track: int, count: int = 1) -> None:
        self.do_command(command=f'SelectTracks:Mode=Set Track={track} TrackCount={count}')

    def remove_tracks(self) -> None:
        self.do_command(command='RemoveTracks')

    def cut_audio(self) -> None:
        self.do_command(command='Cut')

    def paste_audio(self) -> None:
        self.do_command(command='Paste')

    def delete_audio(self) -> None:
        self.do_command(command='Delete')

    def export_audio(self, output_path: str) -> None:
        export_command = 'Export2: Filename={}'.format(output_path)
        self.do_command(command=export_command)
        time.sleep(5)

    def stop_audacity(self) -> None:
        self._client.write(command='Exit')

    def do_command(self, command: str) -> str:
        _LOGGER.debug(f'Sending command to Audacity: {command}')
        self._client.write(command=command, timer=True)
        response = self._client.read()
        _LOGGER.debug(f'Received response from Audacity: {response}')
        time.sleep(0.4)
        return response

    # def _send_command(self, command: str) -> None:
    #     if not self._TOFILE:
    #         raise ValueError('Communication pipe to Audacity is not opened. Ensure _open_pipes() was called.')

    #     _LOGGER.debug(f'Sending command to Audacity: {command}')
    #     self._TOFILE.write(command + self._EOL)
    #     self._TOFILE.flush()

    # def _get_response(self) -> str:
    #     if not self._FROMFILE:
    #         raise ValueError('Communication pipe to Audacity is not opened. Ensure _open_pipes() was called.')

    #     lines = []
    #     while True:
    #         line = self._FROMFILE.readline()
    #         if line == self._EOL:
    #             break
    #         lines.append(line)

    #     return ''.join(lines).strip()

    # def _open_pipes(self) -> None:
    #     self._close_pipes()

    #     if not os.path.exists(self._TONAME):
    #         _LOGGER.error(f'{self._TONAME} does not exist. Ensure Audacity is running with mod-script-pipe.')
    #         raise FileNotFoundError(f'{self._TONAME} not found.')

    #     if not os.path.exists(self._FROMNAME):
    #         _LOGGER.error(f'{self._FROMNAME} does not exist. Ensure Audacity is running with mod-script-pipe.')
    #         raise FileNotFoundError(f'{self._FROMNAME} not found.')

    #     self._TOFILE = open(self._TONAME, 'w')
    #     self._FROMFILE = open(self._FROMNAME, 'rt')
    #     _LOGGER.info('Communication pipes with Audacity opened successfully.')

    # def _close_pipes(self) -> None:
    #     if self._TOFILE:
    #         self._TOFILE.close()
    #         self._TOFILE = None

    #     if self._FROMFILE:
    #         self._FROMFILE.close()
    #         self._FROMFILE = None

    #     _LOGGER.info('Communication pipes with Audacity closed successfully.')

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
            # out, err = new_process.communicate(timeout=AUDACITY_TIMEOUT_TIME)
            self._client = PipeClient()
            # _LOGGER.debug(f'STDOUT: {out.decode()}')
            # _LOGGER.debug(f'STDERR: {err.decode()}')
        except Exception as e:
            raise RuntimeError('Failed to start Audacity process.') from e

        _LOGGER.debug(f'Audacity process started successfully with pid: {new_process.pid}')
        time.sleep(AUDACITY_WAIT_TIME)

        return new_process.pid
